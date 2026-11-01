# Experiment 10: 3D Viewing Pipeline, Projection and Viewport Mapping

**File:** `exp10.py`

## Overview
This experiment implements the complete **3D Viewing Pipeline** in computer graphics, transforming geometric primitives from 3D object space to a 2D digital screen. The program demonstrates the contrast between **Orthographic Projection** (parallel rays preserving geometric proportions) and **Perspective Projection** (converging rays modeling realistic human depth perception) using side-by-side viewports displaying an animated 3D multi-colored cube with depth buffering.

## Formulas and Operations

### The 3D Viewing Pipeline Stages
The 3D viewing transformation pipeline progresses through six coordinate spaces:
```
[Object Coordinates] 
       │  Model Matrix (M_model)
       ▼
[World Coordinates] 
       │  View Matrix (M_view)
       ▼
[Eye / Camera Coordinates] 
       │  Projection Matrix (M_proj)
       ▼
[Clip Coordinates] 
       │  Perspective Division (/w)
       ▼
[Normalized Device Coordinates (NDC)] 
       │  Viewport Matrix (M_viewport)
       ▼
[Screen / Window Coordinates]
```

### 1. Modeling Transformation ($M_{\text{model}}$)
Positions, scales, and rotates the 3D cube from local object coordinates $(x_o, y_o, z_o)$ into world space $(x_w, y_w, z_w)$ using Euler rotation angles around the diagonal axis $(1, 1, 0)$:
$$P_w = M_{\text{model}} \cdot P_o$$

### 2. View Transformation ($M_{\text{view}}$)
Transforms world coordinates into eye/camera coordinates where the camera sits at origin $(0, 0, 0)$ looking down the $-Z$ axis:
$$\text{Camera Position: } \vec{E} = (4, 3, 6), \quad \text{Look-At Point: } \vec{C} = (0, 0, 0), \quad \text{Up Vector: } \vec{U} = (0, 1, 0)$$

The camera coordinate axes are formulated as:
$$\vec{z}_c = \frac{\vec{E} - \vec{C}}{\|\vec{E} - \vec{C}\|}, \quad \vec{x}_c = \frac{\vec{U} \times \vec{z}_c}{\|\vec{U} \times \vec{z}_c\|}, \quad \vec{y}_c = \vec{z}_c \times \vec{x}_c$$

$$M_{\text{view}} = \begin{bmatrix} x_{cx} & x_{cy} & x_{cz} & -\vec{x}_c \cdot \vec{E} \\ y_{cx} & y_{cy} & y_{cz} & -\vec{y}_c \cdot \vec{E} \\ z_{cx} & z_{cy} & z_{cz} & -\vec{z}_c \cdot \vec{E} \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

### 3. Projection Transformations ($M_{\text{proj}}$)

#### A. Orthographic Projection (`glOrtho`)
All projection rays are parallel to the viewing direction. True geometric scale and parallel lines are preserved without foreshortening:
$$M_{\text{ortho}} = \begin{bmatrix} \frac{2}{r - l} & 0 & 0 & -\frac{r + l}{r - l} \\ 0 & \frac{2}{t - b} & 0 & -\frac{t + b}{t - b} \\ 0 & 0 & -\frac{2}{f - n} & -\frac{f + n}{f - n} \\ 0 & 0 & 0 & 1 \end{bmatrix}$$

#### B. Perspective Projection (`gluPerspective`)
Projector rays converge towards the center of projection (the eye). Objects further away project smaller, producing depth foreshortening:
$$M_{\text{persp}} = \begin{bmatrix} \frac{\cot(\text{fovy}/2)}{\text{aspect}} & 0 & 0 & 0 \\ 0 & \cot(\text{fovy}/2) & 0 & 0 \\ 0 & 0 & -\frac{f + n}{f - n} & -\frac{2fn}{f - n} \\ 0 & 0 & -1 & 0 \end{bmatrix}$$

### 4. Perspective Division & NDC
Clip space coordinates $[x_c, y_c, z_c, w_c]^T$ are converted to Normalized Device Coordinates (NDC) in $[-1, 1]^3$:
$$x_{\text{ndc}} = \frac{x_c}{w_c}, \quad y_{\text{ndc}} = \frac{y_c}{w_c}, \quad z_{\text{ndc}} = \frac{z_c}{w_c}$$

### 5. Viewport Mapping ($M_{\text{viewport}}$)
Maps normalized device coordinates $[-1, 1] \times [-1, 1]$ to physical pixel screen coordinates $(x_s, y_s)$ within viewport $[x_v, y_v, w_v, h_v]$:
$$x_s = x_v + \frac{x_{\text{ndc}} + 1}{2} \cdot w_v$$
$$y_s = y_v + \frac{y_{\text{ndc}} + 1}{2} \cdot h_v$$

- **Left Viewport:** $x_v = 0, y_v = 0, w_v = W/2, h_v = H$ (Orthographic)
- **Right Viewport:** $x_v = W/2, y_v = 0, w_v = W/2, h_v = H$ (Perspective)

## Visual Result
<img src="image.png" alt="Experiment 10 - 3D Viewing Pipeline" width="650">

*The image demonstrates the complete 3D viewing pipeline in a side-by-side comparison: the left viewport displays an orthographic projection where parallel cube edges remain strictly parallel without foreshortening (ideal for engineering/CAD), while the right viewport displays a perspective projection with natural foreshortening and vanishing points (modeling real-world human vision).*

## How to Run

```bash
python exp10.py
```

To capture a screenshot and exit headlessly:
```bash
python exp10.py --headless
```

### Controls (Interactive Mode)
- The 3D cube continuously rotates along multiple axes in real time across both viewports simultaneously.
- Press `Esc` or close window to exit.

### Requirements
- Python 3.x
- PyOpenGL
- GLFW (`pip install glfw`)
- Pillow (`pip install pillow`)


---

## Unity Implementation

A Unity 2022.3 LTS C# implementation of the complete 3D Viewing Pipeline is included in `projects/New Unity Project/`.

### Scripts (in `Assets/Scripts/Lab10/`)

| Script | Purpose |
|---|---|
| `Lab10ViewingPipeline.cs` | Runtime camera builder � creates left (Orthographic) and right (Perspective FOV 45) cameras via `Camera.rect` viewport splitting |
| `Lab10RotatingCube.cs` | Rotates the coloured multi-face cube on all three axes continuously |

### Editor Auto-Setup (in `Assets/Editor/Lab10/`)

`Lab10SceneSetup.cs` � run **Lab > Setup Lab 10 Scene** from the Unity menu bar.
Creates: a 6-face coloured rotating cube, dual split-screen cameras, UI labels, a centre divider line, and ambient lighting.

### How to Open & Run

1. Open **Unity Hub** and add the project at `projects/New Unity Project/`
2. Open the project in **Unity 2022.3 LTS**
3. Open an **empty scene** (File > New Scene)
4. In the menu bar select **Lab > Setup Lab 10 Scene**
5. Press **Play**
   - **Left half** � Orthographic projection: parallel edges stay parallel, no foreshortening
   - **Right half** � Perspective projection (FOV 45): realistic depth foreshortening

### Pipeline Stages Demonstrated in Unity

```
[Object Coordinates]  ->  Model Matrix (rotation on all axes)
       |
[World Coordinates]   ->  View Matrix (camera look-at)
       |
[Eye Coordinates]     ->  Projection Matrix (Ortho left | Perspective right)
       |
[Clip Coordinates]    ->  Perspective Division (/w)
       |
[NDC -1..1]           ->  Viewport Matrix (Camera.rect splits screen 50/50)
       |
[Screen Pixels]
```