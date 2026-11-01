using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Experiment 10 — Auto-Bootstrap
/// Automatically builds the Lab 10 dual-projection scene at runtime when Play is pressed.
/// No setup menu needed — just open the project and press Play.
/// Uses [RuntimeInitializeOnLoadMethod] so it fires even in an empty scene.
/// </summary>
public class Lab10Bootstrap
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    static void Bootstrap()
    {
        Debug.Log("[Lab 10] Auto-bootstrapping 3D Viewing Pipeline scene...");

        // ── Lighting ───────────────────────────────────────────────────────
        GameObject lightGO = new GameObject("Directional Light");
        Light light = lightGO.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.3f;
        lightGO.transform.rotation = Quaternion.Euler(45f, -45f, 0f);

        // ── Coloured multi-face cube ───────────────────────────────────────
        // We use a standard Cube and apply a per-face colored child quad approach
        // so each face shows a distinct colour even under default lighting.
        GameObject cube = new GameObject("Lab10Cube");
        cube.tag = "Lab10Cube";
        cube.transform.position = Vector3.zero;

        (Vector3 dir, Color col)[] faces = {
            (Vector3.up,      new Color(0.9f, 0.2f, 0.2f)),   // top    – red
            (Vector3.down,    new Color(1.0f, 0.6f, 0.0f)),   // bottom – orange
            (Vector3.forward, new Color(0.2f, 0.8f, 0.2f)),   // front  – green
            (Vector3.back,    new Color(0.2f, 0.4f, 1.0f)),   // back   – blue
            (Vector3.right,   new Color(0.9f, 0.9f, 0.1f)),   // right  – yellow
            (Vector3.left,    new Color(0.7f, 0.2f, 0.9f)),   // left   – purple
        };
        foreach (var (dir, col) in faces)
        {
            GameObject quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.Destroy(quad.GetComponent<MeshCollider>());
            quad.transform.SetParent(cube.transform);
            quad.transform.localPosition = dir * 0.505f;   // just outside cube surface
            quad.transform.localRotation = Quaternion.LookRotation(dir);
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = col;
            quad.GetComponent<Renderer>().material = mat;
        }
        cube.AddComponent<Lab10RotatingCube>().rotationSpeed = new Vector3(20f, 35f, 10f);

        // ── Disable any existing cameras so only ours run ──────────────────
        foreach (var cam in Object.FindObjectsOfType<Camera>())
            cam.enabled = false;

        // Remove any existing AudioListeners to avoid duplicate warnings
        foreach (var al in Object.FindObjectsOfType<AudioListener>())
            Object.Destroy(al);

        // ── Left camera — Orthographic ─────────────────────────────────────
        GameObject orthoCamGO = new GameObject("OrthoCamera");
        Camera orthoCam = orthoCamGO.AddComponent<Camera>();
        orthoCamGO.transform.position = new Vector3(4f, 3f, 7f);
        orthoCamGO.transform.LookAt(Vector3.zero);
        orthoCam.orthographic     = true;
        orthoCam.orthographicSize = 2.5f;
        orthoCam.rect             = new Rect(0f, 0f, 0.5f, 1f);
        orthoCam.depth            = 0;
        orthoCam.nearClipPlane    = 0.1f;
        orthoCam.farClipPlane     = 100f;
        orthoCamGO.AddComponent<AudioListener>();

        // ── Right camera — Perspective ─────────────────────────────────────
        GameObject perspCamGO = new GameObject("PerspCamera");
        Camera perspCam = perspCamGO.AddComponent<Camera>();
        perspCamGO.transform.position = new Vector3(4f, 3f, 7f);
        perspCamGO.transform.LookAt(Vector3.zero);
        perspCam.orthographic  = false;
        perspCam.fieldOfView   = 45f;
        perspCam.rect          = new Rect(0.5f, 0f, 0.5f, 1f);
        perspCam.depth         = 1;
        perspCam.clearFlags    = CameraClearFlags.Depth;   // share skybox from ortho cam
        perspCam.nearClipPlane = 0.1f;
        perspCam.farClipPlane  = 100f;

        // ── UI Labels Canvas ───────────────────────────────────────────────
        GameObject canvasGO = new GameObject("Labels Canvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvasGO.AddComponent<CanvasScaler>();
        canvasGO.AddComponent<GraphicRaycaster>();

        // Left label
        MakeText(canvasGO, "OrthoLabel",
            "Orthographic Projection\n(Parallel rays - no foreshortening)",
            22, Color.white, FontStyle.Bold,
            new Vector2(0f, 1f), new Vector2(0f, 1f),
            new Vector2(16f, -16f), new Vector2(440f, 70f));

        // Right label
        MakeText(canvasGO, "PerspLabel",
            "Perspective Projection\n(Converging rays - depth foreshortening)",
            22, new Color(1f, 0.95f, 0.5f), FontStyle.Bold,
            new Vector2(0.5f, 1f), new Vector2(0.5f, 1f),
            new Vector2(16f, -16f), new Vector2(440f, 70f));

        // Bottom title
        MakeText(canvasGO, "TitleLabel",
            "Experiment 10: 3D Viewing Pipeline — Orthographic vs Perspective",
            18, new Color(1f, 1f, 1f, 0.8f), FontStyle.Normal,
            new Vector2(0.5f, 0f), new Vector2(0.5f, 0f),
            new Vector2(0f, 16f), new Vector2(760f, 36f),
            TextAnchor.MiddleCenter);

        // Centre divider (thin black image)
        GameObject divider = new GameObject("Divider");
        divider.transform.SetParent(canvasGO.transform, false);
        Image img = divider.AddComponent<Image>();
        img.color = Color.black;
        RectTransform drt = divider.GetComponent<RectTransform>();
        drt.anchorMin = new Vector2(0.5f, 0f);
        drt.anchorMax = new Vector2(0.5f, 1f);
        drt.pivot     = new Vector2(0.5f, 0.5f);
        drt.anchoredPosition = Vector2.zero;
        drt.sizeDelta = new Vector2(3f, 0f);

        Debug.Log("[Lab 10] Scene ready! Left = Orthographic, Right = Perspective.");
    }

    // ── Helper ─────────────────────────────────────────────────────────────
    static Text MakeText(GameObject canvasGO, string name, string content,
        int fontSize, Color color, FontStyle style,
        Vector2 anchorMin, Vector2 anchorMax,
        Vector2 anchoredPos, Vector2 size,
        TextAnchor alignment = TextAnchor.UpperLeft)
    {
        GameObject go = new GameObject(name);
        go.transform.SetParent(canvasGO.transform, false);
        Text t = go.AddComponent<Text>();
        t.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.text      = content;
        t.fontSize  = fontSize;
        t.color     = color;
        t.fontStyle = style;
        t.alignment = alignment;
        RectTransform rt = go.GetComponent<RectTransform>();
        rt.anchorMin = anchorMin;
        rt.anchorMax = anchorMax;
        rt.pivot     = anchorMin;
        rt.anchoredPosition = anchoredPos;
        rt.sizeDelta = size;
        return t;
    }
}
