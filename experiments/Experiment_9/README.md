# Experiment 9: Simple Interactive 3D Scene

**File:** `exp9.py`

## Overview
This experiment demonstrates the design and implementation of a **simple interactive 3D scene**, fulfilling both the core virtual reality / real-time graphics principles and game engine architectural patterns (such as those used in Unity). The program constructs a 3D virtual environment complete with an arena floor grid, a movable player avatar, third-person smooth camera tracking, 3D obstacle blocks, rotating animated collectible gems, collision detection, and a real-time Heads-Up Display (HUD).

## Formulas and Operations

### 1. Player Kinematics & Jump Physics
The player avatar is modeled as a rigid bounding box moving across the horizontal $XZ$-plane with vertical gravity simulation along the $Y$-axis:

#### Horizontal Velocity & Heading
Given player orientation angle $\theta$ (yaw in radians) and speed $v$:
$$\Delta x = -v \cdot \Delta t \cdot \sin(\theta)$$
$$\Delta z = v \cdot \Delta t \cdot \cos(\theta)$$
$$x_{t+\Delta t} = x_t + \Delta x, \quad z_{t+\Delta t} = z_t + \Delta z$$

#### Vertical Gravity & Jumping
Using Euler numerical integration with gravitational acceleration $g = 24.0 \text{ m/s}^2$:
$$v_y(t + \Delta t) = v_y(t) - g \cdot \Delta t$$
$$y(t + \Delta t) = y(t) + v_y(t) \cdot \Delta t$$
When grounded ($y \le y_{\text{ground}}$):
$$y = y_{\text{ground}}, \quad v_y = 0, \quad \text{is\_grounded} = \text{True}$$
Triggering jump applies instantaneous impulse velocity: $v_y = v_{\text{jump}} = 8.5 \text{ m/s}$.

### 2. Third-Person Following Camera Pipeline
A dynamic third-person camera tracks the player's position $(P_x, P_y, P_z)$ while maintaining an offset distance $d_{\text{cam}} = 6.0$ and elevation $h_{\text{cam}} = 3.2$:
$$C_x = P_x - d_{\text{cam}} \cdot \sin(\theta)$$
$$C_z = P_z + d_{\text{cam}} \cdot \cos(\theta)$$
$$C_y = P_y + h_{\text{cam}}$$

The viewing transformation is computed via `gluLookAt`:
$$\text{Camera Position: } \vec{C} = (C_x, C_y, C_z)$$
$$\text{Target / Look-At Point: } \vec{T} = (P_x, P_y + 0.6, P_z)$$
$$\text{Up Vector: } \vec{Up} = (0, 1, 0)$$

### 3. Rotating Collectible Animation & Collision
- **Continuous Rotation:** Each gem rotates continuously around its local vertical axis:
  $$\phi(t) = \omega \cdot t \quad (\omega = 75^\circ/\text{s})$$
- **Harmonic Bobbing:** Floating gems oscillate harmonically above the ground:
  $$y_{\text{gem}}(t) = y_0 + A \cdot \sin(\omega_{\text{bob}} \cdot t + \phi_0)$$
- **Proximity Collision Detection:** A collectible is gathered when Euclidean distance falls below pickup radius $R_{\text{pickup}} = 1.3\text{m}$:
  $$\text{dist} = \sqrt{(P_x - C_x)^2 + (P_z - C_z)^2} < R_{\text{pickup}}$$

### 4. Unity Architecture Comparison
The implementation directly mirrors the component-based architecture of Unity 3D:
- **GameObjects & Transforms:** Hierarchy of player, arena, camera, obstacles, and gems.
- **Character Controller (`PlayerController.cs`):** Manages input handling, kinematic velocity, and jump mechanics.
- **Camera Rig (`CameraFollow.cs`):** Smooth third-person following system using lerp/look-at transforms.
- **Rotator & Collectible (`RotatingObject.cs`, `Collectible.cs`):** Trigger colliders and continuous rotation scripts.
- **Canvas / HUD (`GameHUD.cs`):** Real-time UI displaying collected items count and objective status.

## Visual Result
<img src="image.png" alt="Experiment 9 - Simple Interactive 3D Scene" width="650">

*The image shows the interactive 3D scene in real time: a third-person view of the player avatar navigating a checkered arena floor, surrounded by 3D obstacles and rotating collectible diamond gems, accompanied by an integrated Heads-Up Display (HUD) showing collectibles gathered, player telemetry, and interactive control bindings.*

## How to Run

```bash
python exp9.py
```

To capture a screenshot and exit headlessly:
```bash
python exp9.py --headless
```

### Controls (Interactive Mode)
- **`W` / `Up Arrow`**: Move forward
- **`S` / `Down Arrow`**: Move backward
- **`A` / `Left Arrow`**: Turn left
- **`D` / `Right Arrow`**: Turn right
- **`Space`**: Jump
- **`R`**: Reset player position and respawn collectibles
- **`Esc`**: Exit scene

### Requirements
- Python 3.x
- PyOpenGL
- GLFW (`pip install glfw`)
- Pillow (`pip install pillow`)

