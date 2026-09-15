# Autonomous racetrack simulator — runs in the browser via Pyodide.
# Vehicle: kinematic bicycle model. State = [x, y, phi (heading), v, theta (steer angle)].
# Controls  = [a (accel), theta_dot (steer rate)]. Units: pixels, seconds, radians.
import math

PARAMS = dict(
    K_h=2.4,          # heading-error gain
    K_l=0.035,        # lateral-error gain (rad per px)
    K_s=9.0,          # steering-rate gain (rad/s per rad)
    K_v=1.6,          # speed P gain
    v_max=190.0,      # px/s
    a_lat=280.0,      # max lateral accel budget for corner speed, px/s^2
    a_max=140.0,      # accel limit, px/s^2
    b_max=260.0,      # braking limit, px/s^2
    L=22.0,           # wheelbase, px
    theta_max=0.6,    # max steer angle, rad
    thetadot_max=4.0, # max steer rate, rad/s
    lookahead=16.0,   # px ahead for heading target (scaled by speed)
    look_v=0.10,      # extra lookahead per px/s of speed
    ahead_pts=28,     # points scanned ahead for corner curvature
)


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def controller(state, err, p):
    """USER-EDITABLE. Returns (a, theta_dot).
    state: x, y, phi, v, theta
    err:   e_head (rad, +ve = target is to the left in screen coords),
           e_lat  (px, +ve = car is left of the centerline), kappa_ahead (1/px)
    """
    x, y, phi, v, theta = state
    # Steering: point at the lookahead target, and pull back toward the centerline
    theta_des = p['K_h'] * err['e_head'] - p['K_l'] * err['e_lat']
    theta_des = max(-p['theta_max'], min(p['theta_max'], theta_des))
    theta_dot = p['K_s'] * (theta_des - theta)
    # Speed: slow down for the tightest corner coming up (v = sqrt(a_lat / kappa))
    v_target = min(p['v_max'], math.sqrt(p['a_lat'] / max(err['kappa_ahead'], 1e-5)))
    a = p['K_v'] * (v_target - v)
    return a, theta_dot


class Sim:
    def __init__(self):
        self.p = dict(PARAMS)
        self.track = []
        self.tan = []
        self.kappa = []
        self.n = 0
        self.half_w = 30.0
        self.state = [0.0, 0.0, 0.0, 0.0, 0.0]
        self.idx = 0
        self.laps = 0
        self.lap_time = 0.0
        self.best_lap = None
        self.t = 0.0
        self.off_track = 0
        self.was_off = False
        self.running = False
        self.started = False

    # ---- track -------------------------------------------------------------
    def set_track(self, pts, half_w):
        self.track = [(float(a), float(b)) for a, b in pts]
        self.n = len(self.track)
        self.half_w = float(half_w)
        n = self.n
        self.tan = []
        self.kappa = []
        for i in range(n):
            x0, y0 = self.track[(i - 1) % n]
            x1, y1 = self.track[(i + 1) % n]
            dx, dy = x1 - x0, y1 - y0
            d = math.hypot(dx, dy) or 1.0
            self.tan.append((dx / d, dy / d))
        for i in range(n):
            t0 = self.tan[(i - 1) % n]
            t1 = self.tan[(i + 1) % n]
            dphi = wrap(math.atan2(t1[1], t1[0]) - math.atan2(t0[1], t0[0]))
            x0, y0 = self.track[(i - 1) % n]
            x1, y1 = self.track[(i + 1) % n]
            ds = math.hypot(x1 - x0, y1 - y0) or 1.0
            self.kappa.append(abs(dphi) / ds)
        self.reset()

    def reset(self):
        if self.n:
            x, y = self.track[0]
            tx, ty = self.tan[0]
            self.state = [x, y, math.atan2(ty, tx), 0.0, 0.0]
        self.idx = 0
        self.laps = 0
        self.lap_time = 0.0
        self.best_lap = None
        self.t = 0.0
        self.off_track = 0
        self.was_off = False
        self.started = False

    def set_param(self, k, v):
        self.p[k] = float(v)

    def set_width(self, half_w):
        self.half_w = float(half_w)

    # ---- helpers -----------------------------------------------------------
    def closest(self, x, y):
        n = self.n
        best, bi = 1e18, self.idx
        # local window first (fast, avoids jumping across the track)
        for k in range(-20, 41):
            i = (self.idx + k) % n
            px, py = self.track[i]
            d = (px - x) ** 2 + (py - y) ** 2
            if d < best:
                best, bi = d, i
        if best > (self.half_w * 4) ** 2:  # lost: global search
            for i in range(n):
                px, py = self.track[i]
                d = (px - x) ** 2 + (py - y) ** 2
                if d < best:
                    best, bi = d, i
        return bi

    def errors(self, x, y, phi, v):
        i = self.closest(x, y)
        px, py = self.track[i]
        tx, ty = self.tan[i]
        e_lat = tx * (y - py) - ty * (x - px)          # signed cross product
        look = self.p['lookahead'] + self.p['look_v'] * v
        # walk forward along the centerline by `look` px
        j, acc = i, 0.0
        while acc < look:
            k = (j + 1) % self.n
            ax, ay = self.track[j]
            bx, by = self.track[k]
            acc += math.hypot(bx - ax, by - ay)
            j = k
            if j == i:
                break
        lx, ly = self.track[j]
        e_head = wrap(math.atan2(ly - y, lx - x) - phi)
        kap = 0.0
        for k in range(int(self.p['ahead_pts'])):
            kap = max(kap, self.kappa[(i + k) % self.n])
        return i, dict(e_lat=e_lat, e_head=e_head, kappa_ahead=kap, look=(lx, ly))

    # ---- integration --------------------------------------------------------
    def step(self, n_sub, dt):
        p = self.p
        out = None
        for _ in range(n_sub):
            x, y, phi, v, theta = self.state
            i, err = self.errors(x, y, phi, v)
            a, thd = controller((x, y, phi, v, theta), err, p)
            a = max(-p['b_max'], min(p['a_max'], a))
            thd = max(-p['thetadot_max'], min(p['thetadot_max'], thd))
            # integrate kinematic bicycle
            x += v * math.cos(phi) * dt
            y += v * math.sin(phi) * dt
            phi = wrap(phi + (v / p['L']) * math.tan(theta) * dt)
            v = max(0.0, v + a * dt)
            theta = max(-p['theta_max'], min(p['theta_max'], theta + thd * dt))
            self.state = [x, y, phi, v, theta]
            # lap / progress bookkeeping
            prev = self.idx
            self.idx = i
            self.t += dt
            if self.started:
                self.lap_time += dt
            if prev > self.n * 0.85 and i < self.n * 0.15:
                if self.started:
                    self.laps += 1
                    if self.best_lap is None or self.lap_time < self.best_lap:
                        self.best_lap = self.lap_time
                    self.lap_time = 0.0
                self.started = True
            elif not self.started and i > 2:
                self.started = True
                self.lap_time = 0.0
            off = abs(err['e_lat']) > self.half_w
            if off and not self.was_off:
                self.off_track += 1
            self.was_off = off
            out = err
        x, y, phi, v, theta = self.state
        return [x, y, phi, v, theta, out['e_lat'], out['e_head'], self.idx, self.laps,
                self.lap_time, self.best_lap if self.best_lap is not None else -1.0,
                self.off_track, out['look'][0], out['look'][1], out['kappa_ahead']]


sim = Sim()
