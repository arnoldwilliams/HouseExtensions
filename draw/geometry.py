"""
geometry.py - real-world geometry helpers layered on top of svgkit.

A `View` maps real building millimetres onto paper millimetres for one drawing
on a sheet, so the drawing code can be written in building coordinates and the
scale / position handled in one place.
"""

from __future__ import annotations

import math

import svgkit as sk


class View:
    def __init__(self, sheet, k, ox, oy, yflip=True, clip=None):
        self.s = sheet
        self.k = k
        self.ox = ox
        self.oy = oy
        self.yflip = yflip
        self.clip = clip          # (x0, y0, x1, y1) paper clip rect, optional

    # ---- coordinate mapping -------------------------------------------
    def X(self, x):
        return self.ox + x * self.k

    def Y(self, y):
        return self.oy - y * self.k if self.yflip else self.oy + y * self.k

    def L(self, v):
        return v * self.k

    # ---- primitives in real coordinates -------------------------------
    def line(self, x1, y1, x2, y2, **kw):
        self.s.line(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), **kw)

    def rect(self, x, y, w, h, **kw):
        """x,y = real lower-left corner (pre-flip); w,h real size."""
        px = self.X(x)
        py = self.Y(y + h) if self.yflip else self.Y(y)
        self.s.rect(px, py, w * self.k, h * self.k, **kw)

    def poly(self, pts, **kw):
        self.s.poly([(self.X(x), self.Y(y)) for x, y in pts], **kw)

    def circle(self, cx, cy, r, **kw):
        self.s.circle(self.X(cx), self.Y(cy), r * self.k, **kw)

    def text(self, x, y, s, size=2.5, anchor="start", weight="normal",
             cls=None, rotate=None, fill=None):
        self.s.text(self.X(x), self.Y(y), s, size=size, anchor=anchor,
                    weight=weight, cls=cls, rotate=rotate, fill=fill)

    def path(self, d, **kw):
        self.s.path(d, **kw)

    def dim(self, x1, y1, x2, y2, label, offset=1200.0, side=1, size=2.2):
        self.s.dim(self.X(x1), self.Y(y1), self.X(x2), self.Y(y2), label,
                   offset=offset * self.k, side=side, size=size)

    def dim_h(self, y, x1, x2, label, offset=1200.0, side=1, size=2.2):
        self.dim(x1, y, x2, y, label, offset=offset, side=side, size=size)

    def dim_v(self, x, y1, y2, label, offset=1200.0, side=1, size=2.2):
        self.dim(x, y1, x, y2, label, offset=offset, side=side, size=size)

    # ---- walls ---------------------------------------------------------
    def wall(self, x0, y0, x1, y1, t, fill=sk.NEW_FILL, sw=sk.LW_THICK,
             openings=None, stroke=sk.INK):
        """Axis-aligned wall centreline with optional openings.

        openings: list of (a, b, kind, opts) measured from (x0,y0) along the
        wall, where kind is 'win', 'door', 'opening' or 'none'.
        """
        horiz = abs(y1 - y0) < 1e-6
        L = (x1 - x0) if horiz else (y1 - y0)
        sign = 1.0 if L >= 0 else -1.0
        total = abs(L)
        segs = []
        cur = 0.0
        ops = sorted(openings or [], key=lambda o: o[0])
        for (a, b, kind, opts) in ops:
            a = max(0.0, a)
            b = min(total, b)
            if a > cur:
                segs.append((cur, a))
            cur = max(cur, b)
        if cur < total:
            segs.append((cur, total))

        def wall_seg(a, b):
            if b - a < 1e-6:
                return
            if horiz:
                xa = x0 + sign * a
                xb = x0 + sign * b
                self.rect(min(xa, xb), y0 - t / 2, abs(xb - xa), t,
                          fill=fill, stroke=stroke, sw=sw)
            else:
                ya = y0 + sign * a
                yb = y0 + sign * b
                self.rect(x0 - t / 2, min(ya, yb), t, abs(yb - ya),
                          fill=fill, stroke=stroke, sw=sw)

        for (a, b) in segs:
            wall_seg(a, b)
        # jambs at openings + symbols
        for (a, b, kind, opts) in ops:
            a = max(0.0, a)
            b = min(total, b)
            if kind == "win":
                self._window_plan(x0, y0, sign, horiz, a, b, t, opts)
            elif kind == "door":
                self._door_plan(x0, y0, sign, horiz, a, b, t, opts)
            elif kind == "slider":
                self._slider_plan(x0, y0, sign, horiz, a, b, t, opts)
            elif kind == "removed":
                p1 = self._pt(x0, y0, sign, horiz, a)
                p2 = self._pt(x0, y0, sign, horiz, b)
                self.line(p1[0], p1[1], p2[0], p2[1], w=sk.LW_THIN,
                          stroke=sk.MID, dash="2.5,1.5")

    def _pt(self, x0, y0, sign, horiz, d, across=0.0):
        """Point at distance d along wall and `across` perpendicular."""
        if horiz:
            return (x0 + sign * d, y0 + across)
        return (x0 + across, y0 + sign * d)

    def _window_plan(self, x0, y0, sign, horiz, a, b, t, opts):
        # frame lines along the reveal
        p1 = self._pt(x0, y0, sign, horiz, a)
        p2 = self._pt(x0, y0, sign, horiz, b)
        # two glazing lines inside the wall thickness
        for off in (-t / 2 + 40, t / 2 - 40):
            q1 = self._pt(x0, y0, sign, horiz, a, off)
            q2 = self._pt(x0, y0, sign, horiz, b, off)
            self.line(q1[0], q1[1], q2[0], q2[1], w=sk.LW_THIN, stroke=sk.INK)
        # reveal ends
        for d in (a, b):
            r1 = self._pt(x0, y0, sign, horiz, d, -t / 2)
            r2 = self._pt(x0, y0, sign, horiz, d, t / 2)
            self.line(r1[0], r1[1], r2[0], r2[1], w=sk.LW_THIN, stroke=sk.INK)

    def _door_plan(self, x0, y0, sign, horiz, a, b, t, opts):
        width = abs(b - a)
        hinge_at_b = opts.get("hinge", "a") == "b"
        swing = opts.get("swing", 1)   # +1 / -1 which side it opens to
        leaf_len = width
        hd = b if hinge_at_b else a
        hinge = self._pt(x0, y0, sign, horiz, hd)
        # leaf line perpendicular to wall
        tip = (hinge[0], hinge[1] + swing * leaf_len) if horiz else \
              (hinge[0] + swing * leaf_len, hinge[1])
        self.line(hinge[0], hinge[1], tip[0], tip[1], w=sk.LW_THIN, stroke=sk.INK)
        # swing arc
        r = leaf_len * self.k
        cx, cy = self.X(hinge[0]), self.Y(hinge[1])
        tx, ty = self.X(tip[0]), self.Y(tip[1])
        other = self._pt(x0, y0, sign, horiz, a if hinge_at_b else b)
        ox_, oy_ = self.X(other[0]), self.Y(other[1])
        a0 = math.degrees(math.atan2(ty - cy, tx - cx))
        a1 = math.degrees(math.atan2(oy_ - cy, ox_ - cx))
        sweep = 1 if (a1 - a0) % 360 < 180 else 0
        self.s.path(
            f"M {sk.fmt(tx)} {sk.fmt(ty)} A {sk.fmt(r)} {sk.fmt(r)} 0 0 "
            f"{sweep} {sk.fmt(ox_)} {sk.fmt(oy_)}",
            stroke=sk.MID, sw=sk.LW_THIN)

    def _slider_plan(self, x0, y0, sign, horiz, a, b, t, opts):
        # two overlapping leaf rectangles
        mid = (a + b) / 2
        for (s0, s1, off) in ((a, mid + 200, -t / 4), (mid - 200, b, t / 4)):
            p1 = self._pt(x0, y0, sign, horiz, s0, off)
            p2 = self._pt(x0, y0, sign, horiz, s1, off)
            if horiz:
                self.line(p1[0], p1[1], p2[0], p2[1], w=sk.LW_MED, stroke=sk.INK)
            else:
                self.line(p1[0], p1[1], p2[0], p2[1], w=sk.LW_MED, stroke=sk.INK)

    # ---- labels --------------------------------------------------------
    def room(self, x, y, name, area_m2=None, sub=None):
        self.text(x, y, name, size=2.6, anchor="middle", cls="t-room")
        if area_m2 is not None:
            self.text(x, y - 700, f"{area_m2:.1f} m²", size=2.1, anchor="middle",
                      cls="t-area")
        if sub:
            self.text(x, y + 700, sub, size=1.9, anchor="middle", cls="t-area")


def dims_h(view, y, pts, labels, offset=1200, side=1):
    """Horizontal dimension chain in real coordinates."""
    for i in range(len(pts) - 1):
        view.s.dim(view.X(pts[i]), view.Y(y), view.X(pts[i + 1]), view.Y(y),
                   labels[i], offset=offset * view.k, side=side)


def dims_v(view, x, pts, labels, offset=1200, side=1):
    for i in range(len(pts) - 1):
        view.s.dim(view.X(x), view.Y(pts[i]), view.X(x), view.Y(pts[i + 1]),
                   labels[i], offset=offset * view.k, side=side)


def hatch(view, x, y, w, h, kind="existing"):
    view.rect(x, y, w, h, fill=f"url(#hatch-{kind})", stroke="none", sw=0)
