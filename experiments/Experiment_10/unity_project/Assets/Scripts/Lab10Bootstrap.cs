using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Experiment 10 — Auto-Bootstrap (fixed)
/// Builds the dual-projection viewing pipeline scene on Play.
/// Cube uses 6 solid thin-slab faces so both Ortho and Perspective cameras
/// render it cleanly with no clipping or backface issues.
/// </summary>
public class Lab10Bootstrap
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.AfterSceneLoad)]
    static void Bootstrap()
    {
        // Skip if already set up
        if (GameObject.Find("Lab10Cube") != null) return;

        Debug.Log("[Lab 10] Bootstrapping 3D Viewing Pipeline scene...");

        // ── Lighting ───────────────────────────────────────────────────────
        GameObject lightGO = new GameObject("DirectionalLight");
        Light light = lightGO.AddComponent<Light>();
        light.type        = LightType.Directional;
        light.intensity   = 1.4f;
        light.color       = Color.white;
        lightGO.transform.rotation = Quaternion.Euler(40f, -30f, 0f);

        // Second fill light from opposite side
        GameObject fillGO = new GameObject("FillLight");
        Light fill = fillGO.AddComponent<Light>();
        fill.type      = LightType.Directional;
        fill.intensity = 0.5f;
        fill.color     = new Color(0.7f, 0.85f, 1f);
        fillGO.transform.rotation = Quaternion.Euler(-20f, 150f, 0f);

        // ── Coloured cube: 6 solid thin-slab faces ─────────────────────────
        // Each face is a squashed Cube so it renders correctly from ALL angles
        // in both orthographic and perspective cameras.
        GameObject cube = new GameObject("Lab10Cube");
        cube.tag = "Lab10Cube";
        cube.transform.position = Vector3.zero;

        // (local offset, local scale, colour, name)
        var faceData = new (Vector3 pos, Vector3 scl, Color col, string nm)[] {
            (new Vector3( 0f,    0.51f,  0f),   new Vector3(1f,   0.02f, 1f),   new Color(0.9f, 0.15f, 0.15f), "Top"),
            (new Vector3( 0f,   -0.51f,  0f),   new Vector3(1f,   0.02f, 1f),   new Color(1.0f, 0.55f, 0.0f),  "Bottom"),
            (new Vector3( 0f,    0f,     0.51f), new Vector3(1f,   1f,   0.02f), new Color(0.15f,0.75f, 0.15f), "Front"),
            (new Vector3( 0f,    0f,    -0.51f), new Vector3(1f,   1f,   0.02f), new Color(0.15f,0.35f, 0.9f),  "Back"),
            (new Vector3( 0.51f, 0f,     0f),   new Vector3(0.02f,1f,   1f),    new Color(0.9f, 0.85f, 0.1f),  "Right"),
            (new Vector3(-0.51f, 0f,     0f),   new Vector3(0.02f,1f,   1f),    new Color(0.65f,0.15f, 0.85f), "Left"),
        };

        foreach (var (pos, scl, col, nm) in faceData)
        {
            GameObject face = GameObject.CreatePrimitive(PrimitiveType.Cube);
            face.name = nm + "Face";
            face.transform.SetParent(cube.transform);
            face.transform.localPosition = pos;
            face.transform.localScale    = scl;
            Object.Destroy(face.GetComponent<BoxCollider>());
            ApplyColor(face, col);
        }

        // Rotation script drives the cube continuously
        cube.AddComponent<Lab10RotatingCube>().rotationSpeed = new Vector3(18f, 30f, 8f);

        // ── Disable any pre-existing cameras / audio listeners ─────────────
        foreach (var cam in Object.FindObjectsOfType<Camera>())   cam.enabled = false;
        foreach (var al  in Object.FindObjectsOfType<AudioListener>()) Object.Destroy(al);

        // ── Camera positions ───────────────────────────────────────────────
        // Both cameras look at the cube from the same angle so the comparison
        // is fair. The cube is at origin; we position cameras at (3, 2.5, 5).
        Vector3 camPos    = new Vector3(3f, 2.5f, 5f);
        Vector3 lookTarget = Vector3.zero;

        // LEFT — Orthographic
        GameObject orthoCamGO = new GameObject("OrthoCamera");
        Camera orthoCam = orthoCamGO.AddComponent<Camera>();
        orthoCamGO.transform.position = camPos;
        orthoCamGO.transform.LookAt(lookTarget);
        orthoCam.orthographic     = true;
        orthoCam.orthographicSize = 1.8f;
        orthoCam.rect             = new Rect(0f, 0f, 0.5f, 1f);
        orthoCam.depth            = 0;
        orthoCam.nearClipPlane    = 0.1f;
        orthoCam.farClipPlane     = 100f;
        orthoCam.backgroundColor  = new Color(0.06f, 0.06f, 0.10f);
        orthoCam.clearFlags       = CameraClearFlags.SolidColor;
        orthoCamGO.AddComponent<AudioListener>();

        // RIGHT — Perspective
        GameObject perspCamGO = new GameObject("PerspCamera");
        Camera perspCam = perspCamGO.AddComponent<Camera>();
        perspCamGO.transform.position = camPos;
        perspCamGO.transform.LookAt(lookTarget);
        perspCam.orthographic  = false;
        perspCam.fieldOfView   = 50f;
        perspCam.rect          = new Rect(0.5f, 0f, 0.5f, 1f);
        perspCam.depth         = 1;
        perspCam.nearClipPlane = 0.1f;
        perspCam.farClipPlane  = 100f;
        perspCam.backgroundColor  = new Color(0.06f, 0.06f, 0.10f);
        perspCam.clearFlags       = CameraClearFlags.SolidColor;

        // ── UI Labels ──────────────────────────────────────────────────────
        GameObject canvasGO = new GameObject("LabelsCanvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvasGO.AddComponent<CanvasScaler>();
        canvasGO.AddComponent<GraphicRaycaster>();

        // Left label
        MakeText(canvasGO, "OrthoLabel",
            "Orthographic Projection\nParallel rays — no foreshortening",
            22, Color.white, FontStyle.Bold,
            new Vector2(0f, 1f), new Vector2(0f, 1f),
            new Vector2(16f, -16f), new Vector2(440f, 72f));

        // Right label
        MakeText(canvasGO, "PerspLabel",
            "Perspective Projection\nConverging rays — depth foreshortening",
            22, new Color(1f, 0.95f, 0.45f), FontStyle.Bold,
            new Vector2(0.5f, 1f), new Vector2(0.5f, 1f),
            new Vector2(16f, -16f), new Vector2(440f, 72f));

        // Bottom centre title
        MakeText(canvasGO, "TitleLabel",
            "Experiment 10: 3D Viewing Pipeline — Orthographic vs Perspective",
            18, new Color(1f, 1f, 1f, 0.8f), FontStyle.Normal,
            new Vector2(0.5f, 0f), new Vector2(0.5f, 0f),
            new Vector2(0f, 16f), new Vector2(760f, 36f),
            TextAnchor.MiddleCenter);

        // Thin vertical divider line
        GameObject divider = new GameObject("Divider");
        divider.transform.SetParent(canvasGO.transform, false);
        Image img = divider.AddComponent<Image>();
        img.color = new Color(0.7f, 0.7f, 0.7f, 0.6f);
        RectTransform drt = divider.GetComponent<RectTransform>();
        drt.anchorMin        = new Vector2(0.5f, 0f);
        drt.anchorMax        = new Vector2(0.5f, 1f);
        drt.pivot            = new Vector2(0.5f, 0.5f);
        drt.anchoredPosition = Vector2.zero;
        drt.sizeDelta        = new Vector2(2f, 0f);

        Debug.Log("[Lab 10] Ready. Left = Orthographic  |  Right = Perspective (FOV 50).");
    }

    // ── Helpers ────────────────────────────────────────────────────────────
    static void ApplyColor(GameObject go, Color color)
    {
        Renderer r = go.GetComponent<Renderer>();
        if (r == null) return;
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = color;
        r.material = mat;
    }

    static Text MakeText(GameObject canvasGO, string objName, string content,
        int fontSize, Color color, FontStyle style,
        Vector2 anchorMin, Vector2 anchorMax,
        Vector2 anchoredPos, Vector2 size,
        TextAnchor alignment = TextAnchor.UpperLeft)
    {
        GameObject go = new GameObject(objName);
        go.transform.SetParent(canvasGO.transform, false);
        Text t      = go.AddComponent<Text>();
        t.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.text      = content;
        t.fontSize  = fontSize;
        t.color     = color;
        t.fontStyle = style;
        t.alignment = alignment;
        RectTransform rt    = go.GetComponent<RectTransform>();
        rt.anchorMin        = anchorMin;
        rt.anchorMax        = anchorMax;
        rt.pivot            = anchorMin;
        rt.anchoredPosition = anchoredPos;
        rt.sizeDelta        = size;
        return t;
    }
}
