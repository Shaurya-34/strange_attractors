import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


def lorenz_step(x, y, z, sigma=10, rho=28, beta=8 / 3):
    return sigma * (y - x), x * (rho - z) - y, x * y - beta * z


def rossler_step(x, y, z, a=0.2, b=0.2, c=5.7):
    return -y - z, x + a * y, b + z * (x - c)


def aizawa_step(x, y, z, a=0.95, b=0.7, c=0.6, d=3.5, e=0.25, f=0.1):
    dx = (z - b) * x - d * y
    dy = d * x + (z - b) * y
    dz = c + a * z - (z**3) / 3 - (x**2 + y**2) * (1 + e * z) + f * z * x**3
    return dx, dy, dz


def thomas_step(x, y, z, b=0.208186):
    dx = np.sin(y) - b * x
    dy = np.sin(z) - b * y
    dz = np.sin(x) - b * z
    return dx, dy, dz


def integrate(step_fn, initial, dt, n_steps):
    """Euler-integrate step_fn from `initial` for n_steps, returning an
    (n_steps + 1, 3) array of positions."""
    positions = np.empty((n_steps + 1, 3))
    positions[0] = initial
    x, y, z = initial
    for i in range(n_steps):
        dx, dy, dz = step_fn(x, y, z)
        x, y, z = x + dx * dt, y + dy * dt, z + dz * dt
        positions[i + 1] = x, y, z
    return positions


def setup_axis(ax, positions, title):
    """Fix axis limits once, up front, from the full trajectory's extent.
    Never touched again during animation, so the box can't resize mid-play."""
    xs, ys, zs = positions[:, 0], positions[:, 1], positions[:, 2]
    ax.set_xlim3d(xs.min(), xs.max())
    ax.set_ylim3d(ys.min(), ys.max())
    ax.set_zlim3d(zs.min(), zs.max())
    ax.set_title(title)
    line, = ax.plot([], [], [], linewidth=1)
    marker, = ax.plot([], [], [], "o", color="red", markersize=4)
    return line, marker


def animate_side_by_side(attractors, frame_step=64, fps=30, gif_path="attractors.gif"):

    fig = plt.figure(figsize=(18, 6))
    axes = [fig.add_subplot(1, len(attractors), i + 1, projection="3d")
            for i in range(len(attractors))]
    artists = [setup_axis(ax, positions, title)
               for ax, (positions, title, _) in zip(axes, attractors)]

    n_frames = max(len(positions) for positions, _, _ in attractors)
    frame_indices = range(1, n_frames, frame_step)

    def update(i):
        updated = []
        for (positions, _, speed), (line, marker) in zip(attractors, artists):
            j = min(int(i * speed), len(positions) - 1)
            xs, ys, zs = positions[:, 0], positions[:, 1], positions[:, 2]
            line.set_data(xs[:j], ys[:j])
            line.set_3d_properties(zs[:j])
            marker.set_data([xs[j]], [ys[j]])
            marker.set_3d_properties([zs[j]])
            updated += [line, marker]
        return updated

    # blit=False: mplot3d doesn't reliably support blitting, forcing it on
    # tends to produce silently broken partial redraws rather than a
    # speedup, so it's not worth the risk here.
    anim = FuncAnimation(fig, update, frames=frame_indices, blit=False)
    anim.save(gif_path, writer="pillow", fps=fps)
    plt.close(fig)
    return gif_path


# --- Clifford: a discrete map, not a continuous system ---
# Consecutive points can jump anywhere in the plane, so there's no smooth
# path to animate a dot along. The attractor's shape only emerges once you
# plot hundreds of thousands of points as a dense static scatter.
def clifford_step(x, y, a=-1.4, b=1.6, c=1.0, d=0.7):
    x_new = np.sin(a * y) + c * np.cos(a * x)
    y_new = np.sin(b * x) + d * np.cos(b * y)
    return x_new, y_new


def generate_clifford(initial=(0.1, 0.0), n_points=200_000, **params):
    xs = np.empty(n_points)
    ys = np.empty(n_points)
    x, y = initial
    for i in range(n_points):
        x, y = clifford_step(x, y, **params)
        xs[i] = x
        ys[i] = y
    return xs, ys


def plot_clifford(xs, ys, png_path="clifford.png"):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(xs, ys, s=0.15, c=np.arange(len(xs)), cmap="inferno", alpha=0.4, linewidths=0)
    ax.set_aspect("equal")
    ax.axis("off")
    plt.savefig(png_path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return png_path


if __name__ == "__main__":
    lorenz = integrate(lorenz_step, (0.1001, 0, 0), dt=0.01, n_steps=10_000)
    rossler = integrate(rossler_step, (1, 1, 1), dt=0.02, n_steps=20_000)
    aizawa = integrate(aizawa_step, (0.1, 0, 0), dt=0.01, n_steps=20_000)
    thomas = integrate(thomas_step, (0.1, 0, 0), dt=0.05, n_steps=40_000)

    path = animate_side_by_side([
        (lorenz, "Lorenz Attractor", 0.65),
        (rossler, "Rossler Attractor", 1.15),
        (aizawa, "Aizawa Attractor", 1.0),
        (thomas, "Thomas Attractor", 0.5),
    ])
    print(f"saved animation to {path}")

    cxs, cys = generate_clifford(n_points=500_000)
    cpath = plot_clifford(cxs, cys)
    print(f"saved clifford render to {cpath}")
