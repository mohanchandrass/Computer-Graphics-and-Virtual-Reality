// Editor-only scene builder for Experiment 10.
// Menu: Lab ▶ Setup Lab 10 Scene
// Run ONCE in an empty scene to build the dual-viewport viewing pipeline demo.
#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using UnityEngine.UI;

public class Lab10SceneSetup : Editor
{
    [MenuItem("Lab/Setup Lab 10 Scene")]
    static void SetupLab10Scene()
    {
        // ── Clear scene ──────────────────────────────────────────────────────
        foreach (var go in Object.FindObjectsOfType<GameObject>())
            Object.DestroyImmediate(go);

        // ── Directional light ────────────────────────────────────────────────
        GameObject lightGO = new GameObject("Directional Light");
        Light light = lightGO.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.3f;
        lightGO.transform.rotation = Quaternion.Euler(45f, -45f, 0f);

        // ── Coloured rotating cube ───────────────────────────────────────────
        // Build a cube from 6 child quads so each face can have its own colour.
        GameObject cube = new GameObject("Lab10Cube");
        cube.tag = "Lab10Cube";
        cube.transform.position = Vector3.zero;

        // Six faces: direction, color
        (Vector3 dir, Color col)[] faces = {
            (Vector3.up,      new Color(1f,   0.2f, 0.2f)),   // top    – red
            (Vector3.down,    new Color(1f,   0.6f, 0.0f)),   // bottom – orange
            (Vector3.forward, new Color(0.2f, 0.8f, 0.2f)),   // front  – green
            (Vector3.back,    new Color(0.2f, 0.4f, 1.0f)),   // back   – blue
            (Vector3.right,   new Color(0.9f, 0.9f, 0.1f)),   // right  – yellow
            (Vector3.left,    new Color(0.7f, 0.2f, 0.9f)),   // left   – purple
        };

        foreach (var (dir, col) in faces)
        {
            GameObject quad = GameObject.CreatePrimitive(PrimitiveType.Quad);
            Object.DestroyImmediate(quad.GetComponent<MeshCollider>());
            quad.transform.SetParent(cube.transform);
            quad.transform.localPosition = dir * 0.5f;
            quad.transform.localRotation = Quaternion.LookRotation(dir);
            Material mat = new Material(Shader.Find("Standard"));
            mat.color = col;
            quad.GetComponent<Renderer>().sharedMaterial = mat;
            quad.name = $"Face_{dir}";
        }

        // Add a BoxCollider to the root for physics queries
        BoxCollider bc = cube.AddComponent<BoxCollider>();
        bc.size = Vector3.one;

        // Add rotation script
        Lab10RotatingCube rot = cube.AddComponent<Lab10RotatingCube>();
        rot.rotationSpeed = new Vector3(20f, 35f, 10f);

        // ── Camera host (disabled – Lab10ViewingPipeline spawns real cams) ──
        GameObject camHost = new GameObject("CameraHost");
        Camera camComp = camHost.AddComponent<Camera>();
        camComp.enabled = false;

        Lab10ViewingPipeline pipeline = camHost.AddComponent<Lab10ViewingPipeline>();
        pipeline.cubePivot           = cube.transform;
        pipeline.orthographicSize    = 2.5f;
        pipeline.perspectiveFOV      = 45f;
        pipeline.cameraDistance      = 7f;
        pipeline.cameraHeight        = 3f;

        // AudioListener on camera host
        camHost.AddComponent<AudioListener>();

        // ── UI Labels ────────────────────────────────────────────────────────
        GameObject canvas = new GameObject("Labels Canvas");
        Canvas c = canvas.AddComponent<Canvas>();
        c.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.AddComponent<CanvasScaler>();
        canvas.AddComponent<GraphicRaycaster>();

        AddLabel(canvas, "OrthoLabel",
            "Orthographic Projection\n(Parallel rays – no foreshortening)",
            new Vector2(0f, 1f), new Vector2(0f, 1f), new Vector2(20f, -20f),
            new Vector2(400f, 70f), Color.white, 22);

        AddLabel(canvas, "PerspLabel",
            "Perspective Projection\n(Converging rays – depth foreshortening)",
            new Vector2(0.5f, 1f), new Vector2(0.5f, 1f), new Vector2(20f, -20f),
            new Vector2(400f, 70f), new Color(1f, 0.95f, 0.5f), 22);

        AddLabel(canvas, "TitleLabel",
            "Experiment 10: 3D Viewing Pipeline — Orthographic vs Perspective",
            new Vector2(0.5f, 0f), new Vector2(0.5f, 0f), new Vector2(0f, 20f),
            new Vector2(750f, 40f), new Color(1f, 1f, 1f, 0.8f), 18,
            TextAnchor.MiddleCenter);

        // ── Divider line (thin black cube) ──────────────────────────────────
        // Achieved purely via a UI Image spanning the canvas vertically at centre.
        GameObject divider = new GameObject("Divider");
        divider.transform.SetParent(canvas.transform, false);
        Image img = divider.AddComponent<Image>();
        img.color = Color.black;
        RectTransform drt = divider.GetComponent<RectTransform>();
        drt.anchorMin = new Vector2(0.5f, 0f);
        drt.anchorMax = new Vector2(0.5f, 1f);
        drt.pivot     = new Vector2(0.5f, 0.5f);
        drt.anchoredPosition = Vector2.zero;
        drt.sizeDelta = new Vector2(3f, 0f);  // 3px wide, full height via stretch

        // ── Done ─────────────────────────────────────────────────────────────
        Debug.Log("[Lab 10] Scene built successfully! Press Play to view the pipeline.");
        EditorUtility.DisplayDialog("Lab 10 Setup Complete",
            "Scene built!\n\nPress ▶ Play to run the 3D Viewing Pipeline demo.\n\n" +
            "Left  = Orthographic projection\nRight = Perspective projection (FOV 45°)\n" +
            "The cube rotates continuously on all axes.",
            "OK");
    }

    static void AddLabel(GameObject canvas, string name, string text,
        Vector2 anchorMin, Vector2 anchorMax, Vector2 anchoredPos,
        Vector2 sizeDelta, Color color, int fontSize,
        TextAnchor alignment = TextAnchor.UpperLeft)
    {
        GameObject go = new GameObject(name);
        go.transform.SetParent(canvas.transform, false);
        Text t = go.AddComponent<Text>();
        t.font      = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        t.text      = text;
        t.fontSize  = fontSize;
        t.color     = color;
        t.fontStyle = FontStyle.Bold;
        t.alignment = alignment;
        RectTransform rt = go.GetComponent<RectTransform>();
        rt.anchorMin        = anchorMin;
        rt.anchorMax        = anchorMax;
        rt.pivot            = anchorMin;
        rt.anchoredPosition = anchoredPos;
        rt.sizeDelta        = sizeDelta;
    }
}
#endif
