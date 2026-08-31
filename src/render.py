#!/usr/bin/env python3
"""Tiny z-buffer STL renderer -- purely for visual sanity checks."""
import struct, sys, os, zlib
import numpy as np

def load_stl(path):
    d = open(path, 'rb').read()
    if d[:5] == b'solid' and b'facet' in d[:2000]:
        tris, cur = [], []
        for ln in d.decode('ascii', 'ignore').splitlines():
            w = ln.split()
            if len(w) == 4 and w[0] == 'vertex':
                cur.append([float(x) for x in w[1:]])
                if len(cur) == 3:
                    tris.append(cur); cur = []
        return np.array(tris, dtype=np.float64)
    n = struct.unpack('<I', d[80:84])[0]
    a = np.frombuffer(d[84:84 + n * 50].tobytes() if hasattr(d, 'tobytes') else d[84:84 + n * 50],
                      dtype=np.uint8).reshape(n, 50)
    v = a[:, 12:48].copy().view('<f4').reshape(n, 3, 3)
    return v.astype(np.float64)

def render(objs, direction, up=(0, 0, 1), W=1000, H=1000, bg=(250, 250, 248)):
    d = np.array(direction, float); d /= np.linalg.norm(d)
    up = np.array(up, float)
    if abs(np.dot(d, up)) > 0.99: up = np.array([0, 1, 0], float)
    r = np.cross(d, up); r /= np.linalg.norm(r)   # screen-right = d x up
    u = np.cross(r, d)
    M = np.stack([r, u, d])                      # world -> camera

    allv = np.vstack([t.reshape(-1, 3) for t, _ in objs])
    cam = allv @ M.T
    lo, hi = cam.min(0), cam.max(0)
    ctr = (lo + hi) / 2.0
    span = max(hi[0] - lo[0], hi[1] - lo[1]) * 1.10
    sc = min(W, H) / span

    img = np.zeros((H, W, 3), np.float64); img[:] = bg
    zb = np.full((H, W), np.inf)
    light = np.array([-0.4, -0.55, 0.73]); light /= np.linalg.norm(light)

    for tris, col in objs:
        c = tris @ M.T
        px = (c[:, :, 0] - ctr[0]) * sc + W / 2.0
        py = H / 2.0 - (c[:, :, 1] - ctr[1]) * sc
        pz = c[:, :, 2]
        e1 = tris[:, 1] - tris[:, 0]; e2 = tris[:, 2] - tris[:, 0]
        nr = np.cross(e1, e2)
        ln = np.linalg.norm(nr, axis=1); ln[ln == 0] = 1
        nr /= ln[:, None]
        lam = np.abs(nr @ light)
        shade = 0.30 + 0.70 * lam
        base = np.array(col, float)
        for i in range(len(tris)):
            x0 = int(max(0, np.floor(px[i].min()))); x1 = int(min(W - 1, np.ceil(px[i].max())))
            y0 = int(max(0, np.floor(py[i].min()))); y1 = int(min(H - 1, np.ceil(py[i].max())))
            if x1 < x0 or y1 < y0: continue
            ax, ay = px[i, 0], py[i, 0]; bx, by = px[i, 1], py[i, 1]; cx, cy = px[i, 2], py[i, 2]
            den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
            if abs(den) < 1e-12: continue
            xs = np.arange(x0, x1 + 1); ys = np.arange(y0, y1 + 1)
            X, Y = np.meshgrid(xs, ys)
            w0 = ((by - cy) * (X - cx) + (cx - bx) * (Y - cy)) / den
            w1 = ((cy - ay) * (X - cx) + (ax - cx) * (Y - cy)) / den
            w2 = 1.0 - w0 - w1
            m = (w0 >= -1e-9) & (w1 >= -1e-9) & (w2 >= -1e-9)
            if not m.any(): continue
            z = w0 * pz[i, 0] + w1 * pz[i, 1] + w2 * pz[i, 2]
            sub = zb[y0:y1 + 1, x0:x1 + 1]
            hit = m & (z < sub)
            if not hit.any(): continue
            sub[hit] = z[hit]
            img[y0:y1 + 1, x0:x1 + 1][hit] = np.clip(base * shade[i], 0, 255)
    return img.astype(np.uint8)

def write_png(path, arr):
    H, W, _ = arr.shape
    raw = b''.join(b'\x00' + arr[y].tobytes() for y in range(H))
    def chunk(t, data):
        c = struct.pack('>I', len(data)) + t + data
        return c + struct.pack('>I', zlib.crc32(t + data) & 0xffffffff)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 6)) + chunk(b'IEND', b''))
    open(path, 'wb').write(png)

if __name__ == '__main__':
    OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'export')
    C = {'plate': (188, 194, 203), 'shell': (58, 104, 160),
         'dev': (38, 40, 46), 'mast': (172, 168, 160), 'nut': (198, 148, 62)}
    def L(f): return load_stl(os.path.join(OUT, f))
    plate, shell, shopen = L('back_plate.stl'), L('front_shell.stl'), L('_mesh_shell_open.stl')
    dev, mast, bar = L('_mesh_device.stl'), L('_mesh_mast_stub.stl'), L('luff_nut_bar.stl')
    # camera looks along -X, so the screen (max X) faces us
    scenes = {
      'assembly_closed': ([(mast, C['mast']), (bar, C['nut']), (plate, C['plate']),
                           (dev, C['dev']), (shell, C['shell'])],
                          {'iso': (-1.0, 0.55, -0.40), 'front': (-1, 0.02, -0.02)}),
      'assembly_open':   ([(mast, C['mast']), (bar, C['nut']), (plate, C['plate']),
                           (dev, C['dev']), (shopen, C['shell'])],
                          {'iso': (-1.0, 0.55, -0.40)}),
      'groove_detail':   ([(mast, C['mast']), (bar, C['nut']), (plate, C['plate'])],
                          {'top': (0.15, 0.1, -1.0), 'iso': (-1.0, 0.45, -0.35)}),
      'back_plate':      ([(plate, C['plate'])],
                          {'device_face': (-1.0, 0.5, -0.35), 'tongue': (1.0, 0.5, -0.35)}),
    }
    for name, (objs, views) in scenes.items():
        for vn, d in views.items():
            f = 'render_%s_%s.png' % (name, vn)
            write_png(os.path.join(OUT, f), render(objs, d, W=1100, H=1100))
            print(f)
