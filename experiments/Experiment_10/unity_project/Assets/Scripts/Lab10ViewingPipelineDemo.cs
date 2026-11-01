using System.Collections.Generic;
using UnityEngine;

/// <summary>
/// Lab 10: 3D Viewing Pipeline — One rotating cube, two viewports.
/// Left half = Orthographic Projection (parallel rays, no foreshortening).
/// Right half = Perspective Projection (converging rays, depth foreshortening).
/// Port of the original CGVR 3D viewing pipeline experiment.
/// </summary>
[DisallowMultipleComponent]
public sealed class Lab10ViewingPipelineDemo : MonoBehaviour
{
    public Shader faceShader;
    private Transform cubeRoot;
    private Mesh cubeMesh;
    private Material faceMaterial, edgeMaterial;
    private Camera orthoCamera, perspCamera;
    private bool playing = true, showInfo = true;
    private float angle, speed = 30f, fov = 45f, orthoSize = 3f;
    private GUIStyle header, label;

    // Cube vertices (-1 to +1 on all 3 axes)
    private static readonly Vector3[] V = {
        new Vector3(-1,-1,-1), new Vector3( 1,-1,-1), new Vector3( 1, 1,-1), new Vector3(-1, 1,-1),
        new Vector3(-1,-1, 1), new Vector3( 1,-1, 1), new Vector3( 1, 1, 1), new Vector3(-1, 1, 1)
    };

    // 6 faces (each has 4 vertex indices)
    private static readonly int[][] Faces = {
        new[]{0,1,2,3}, // Back face
        new[]{4,5,6,7}, // Front face
        new[]{0,1,5,4}, // Bottom face
        new[]{2,3,7,6}, // Top face
        new[]{1,2,6,5}, // Right face
        new[]{0,3,7,4}  // Left face
    };

    // 6 distinct face colours matching OpenGL lab reference
    private static readonly Color[] Colors = {
        new Color(1f, 0.2f, 0.2f), // Red
        new Color(0.2f, 1f, 0.3f), // Green
        new Color(0.2f, 0.4f, 1f), // Blue
        new Color(1f, 0.8f, 0.2f), // Yellow
        new Color(0.8f, 0.2f, 1f), // Magenta
        new Color(0.2f, 1f, 1f)   // Cyan
    };

    // 12 wireframe edge outlines
    private static readonly int[,] Edges = {
        {0,1},{1,2},{2,3},{3,0},
        {4,5},{5,6},{6,7},{7,4},
        {0,4},{1,5},{2,6},{3,7}
    };

    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    private static void AutoBootstrap()
    {
        if (FindFirstObjectByType<Lab10ViewingPipelineDemo>() == null)
        {
            var runner = new GameObject("Lab10_ViewingPipeline_Runner");
            runner.AddComponent<Lab10ViewingPipelineDemo>();
            Debug.Log("[Lab 10] Auto-bootstrapped 3D Viewing Pipeline demo.");
        }
    }

    private void Awake()
    {
        // Disable pre-existing cameras in scene to avoid conflicts
        foreach (var cam in FindObjectsByType<Camera>(FindObjectsSortMode.None))
        {
            if (cam != orthoCamera && cam != perspCamera)
                cam.enabled = false;
        }
        foreach (var al in FindObjectsByType<AudioListener>(FindObjectsSortMode.None))
        {
            Destroy(al);
        }

        Shader shader = faceShader != null ? faceShader : Shader.Find("CGVR/Lab10/FaceColors");
        if (shader == null || !shader.isSupported)
        {
            shader = Shader.Find("Sprites/Default");
            if (shader == null) shader = Shader.Find("Unlit/Color");
        }

        BuildCube(shader);
        orthoCamera = BuildCamera("LEFT: Orthographic Camera", new Rect(0f, 0f, 0.5f, 1f), true);
        perspCamera = BuildCamera("RIGHT: Perspective Camera", new Rect(0.5f, 0f, 0.5f, 1f), false);
        orthoCamera.gameObject.AddComponent<AudioListener>();

        ApplyProjectionSettings();
    }

    private void BuildCube(Shader shader)
    {
        cubeRoot = new GameObject("Shared rotating cube - model transform").transform;
        GameObject facesObject = new GameObject("6 coloured faces - 12 triangles");
        facesObject.transform.SetParent(cubeRoot, false);

        var vertices = new List<Vector3>();
        var colors = new List<Color>();
        var indices = new List<int>();

        for (int i = 0; i < 6; i++)
        {
            int start = vertices.Count;
            for (int j = 0; j < 4; j++)
            {
                vertices.Add(V[Faces[i][j]]);
                colors.Add(Colors[i]);
            }
            // 2 triangles per quad face
            indices.Add(start);     indices.Add(start + 1); indices.Add(start + 2);
            indices.Add(start);     indices.Add(start + 2); indices.Add(start + 3);
        }

        cubeMesh = new Mesh { name = "Lab10 six-colour cube" };
        cubeMesh.SetVertices(vertices);
        cubeMesh.SetColors(colors);
        cubeMesh.SetTriangles(indices, 0);
        cubeMesh.RecalculateBounds();
        cubeMesh.RecalculateNormals();

        facesObject.AddComponent<MeshFilter>().sharedMesh = cubeMesh;
        faceMaterial = new Material(shader) { name = "Lab10 RGB face shader" };
        facesObject.AddComponent<MeshRenderer>().sharedMaterial = faceMaterial;

        // Wireframe edges for crisp outlines
        Shader linesShader = Shader.Find("Sprites/Default");
        if (linesShader == null) linesShader = Shader.Find("Unlit/Color");
        if (linesShader != null)
        {
            edgeMaterial = new Material(linesShader) { color = new Color(0.025f, 0.035f, 0.05f) };
            for (int i = 0; i < Edges.GetLength(0); i++)
            {
                GameObject edge = new GameObject("Outline edge " + i);
                edge.transform.SetParent(cubeRoot, false);
                LineRenderer line = edge.AddComponent<LineRenderer>();
                line.sharedMaterial = edgeMaterial;
                line.useWorldSpace = false;
                line.positionCount = 2;
                line.SetPosition(0, V[Edges[i, 0]]);
                line.SetPosition(1, V[Edges[i, 1]]);
                line.startWidth = 0.03f;
                line.endWidth = 0.03f;
                line.startColor = Color.black;
                line.endColor = Color.black;
                line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
                line.receiveShadows = false;
            }
        }
    }

    private Camera BuildCamera(string camName, Rect rect, bool isOrtho)
    {
        GameObject go = new GameObject(camName);
        Camera cam = go.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.SolidColor;
        cam.backgroundColor = new Color(0.045f, 0.065f, 0.10f);
        cam.nearClipPlane = 0.1f;
        cam.farClipPlane = 100f;
        cam.rect = rect;
        cam.orthographic = isOrtho;
        cam.depth = isOrtho ? 0f : 1f;

        // Standard viewing transform: eye at (4, 3, 6), looking at (0, 0, 0)
        go.transform.position = new Vector3(4f, 3f, 6f);
        go.transform.LookAt(Vector3.zero, Vector3.up);
        return cam;
    }

    private void ApplyProjectionSettings()
    {
        if (orthoCamera != null) orthoCamera.orthographicSize = orthoSize;
        if (perspCamera != null) perspCamera.fieldOfView = fov;
    }

    private void ResetDemo()
    {
        angle = 0f;
        speed = 30f;
        fov = 45f;
        orthoSize = 3f;
        playing = true;
    }

    private void Update()
    {
        if (Input.GetKeyDown(KeyCode.Space)) playing = !playing;
        if (Input.GetKeyDown(KeyCode.R)) ResetDemo();
        if (Input.GetKeyDown(KeyCode.H)) showInfo = !showInfo;
        if (Input.GetKeyDown(KeyCode.UpArrow)) speed = Mathf.Clamp(speed + 5f, 0f, 120f);
        if (Input.GetKeyDown(KeyCode.DownArrow)) speed = Mathf.Clamp(speed - 5f, 0f, 120f);

        if (playing)
            angle = Mathf.Repeat(angle + speed * Time.deltaTime, 360f);

        if (cubeRoot != null)
            cubeRoot.rotation = Quaternion.AngleAxis(angle, new Vector3(1f, 1f, 0f).normalized);

        ApplyProjectionSettings();
    }

    private void OnGUI()
    {
        float scale = Mathf.Max(0.55f, Mathf.Min(Screen.width / 1280f, Screen.height / 720f));
        float w = Screen.width / scale;
        float h = Screen.height / scale;

        GUI.matrix = Matrix4x4.TRS(Vector3.zero, Quaternion.identity, Vector3.one * scale);

        if (header == null)
        {
            header = new GUIStyle(GUI.skin.label) { fontSize = 20, fontStyle = FontStyle.Bold };
            header.normal.textColor = Color.white;

            label = new GUIStyle(GUI.skin.label) { fontSize = 14, wordWrap = true };
            label.normal.textColor = new Color(0.82f, 0.89f, 0.97f);
        }

        // Top header banner
        GUI.color = new Color(0.04f, 0.08f, 0.14f, 0.95f);
        GUI.DrawTexture(new Rect(12, 12, w - 24, 123), Texture2D.whiteTexture);
        GUI.color = Color.white;

        GUI.Label(new Rect(28, 19, w - 56, 30), "EXPERIMENT 10   |   3D VIEWING PIPELINE", header);
        GUI.Label(new Rect(28, 52, w / 2f - 34, 30), "LEFT VIEWPORT: ORTHOGRAPHIC (Parallel rays, no foreshortening)", label);
        GUI.Label(new Rect(w / 2f + 12, 52, w / 2f - 42, 30), "RIGHT VIEWPORT: PERSPECTIVE (Converging rays, depth foreshortening)", label);

        if (GUI.Button(new Rect(28, 91, 120, 30), playing ? "Pause (Space)" : "Play (Space)"))
            playing = !playing;

        if (GUI.Button(new Rect(158, 91, 100, 30), "Reset (R)"))
            ResetDemo();

        GUI.Label(new Rect(273, 94, 280, 27), "Angle: " + angle.ToString("F0") + "°   |   Speed: " + speed.ToString("F0") + "°/s", label);

        if (GUI.Button(new Rect(w - 148, 91, 124, 30), showInfo ? "Hide Info (H)" : "Show Info (H)"))
            showInfo = !showInfo;

        // Viewport centre divider line
        GUI.color = new Color(0.25f, 0.44f, 0.65f, 0.75f);
        GUI.DrawTexture(new Rect(w / 2f - 1f, 139, 2f, Mathf.Max(0f, h - 151f)), Texture2D.whiteTexture);
        GUI.color = Color.white;

        // Bottom info / control drawer
        if (showInfo)
        {
            GUI.color = new Color(0.04f, 0.08f, 0.14f, 0.95f);
            GUI.DrawTexture(new Rect(12, h - 121, w - 24, 109), Texture2D.whiteTexture);
            GUI.color = Color.white;

            GUI.Label(new Rect(28, h - 111, w - 56, 27),
                "Pipeline: Model -> World -> View (LookAt) -> Projection (Ortho/Persp) -> NDC -> Viewport [Left: (0,0,0.5,1) | Right: (0.5,0,0.5,1)]", label);

            GUI.Label(new Rect(28, h - 83, 154, 24), "Ortho half-size: " + orthoSize.ToString("F1"), label);
            orthoSize = GUI.HorizontalSlider(new Rect(185, h - 75, Mathf.Max(55, w / 2f - 211), 18), orthoSize, 2.2f, 5f);

            GUI.Label(new Rect(w / 2f + 12, h - 83, 160, 24), "Perspective FOV: " + fov.ToString("F0") + "°", label);
            fov = GUI.HorizontalSlider(new Rect(w / 2f + 174, h - 75, Mathf.Max(55, w / 2f - 211), 18), fov, 30f, 70f);

            GUI.Label(new Rect(28, h - 49, w - 56, 31),
                "Controls: Space = Pause/Resume   |   R = Reset   |   Up/Down = Speed   |   H = Toggle Info", label);
        }

        GUI.matrix = Matrix4x4.identity;
        GUI.color = Color.white;
    }

    private void OnDestroy()
    {
        if (faceMaterial != null) Destroy(faceMaterial);
        if (edgeMaterial != null) Destroy(edgeMaterial);
        if (cubeMesh != null) Destroy(cubeMesh);
    }
}
