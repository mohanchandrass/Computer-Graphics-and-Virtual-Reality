// Editor-only scene builder for Experiment 9.
// Menu: Lab > Setup Lab 9 Scene
// Run ONCE in an empty scene to build the full interactive 3D scene.
// Requires: com.unity.ugui package (added to manifest.json)
#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using UnityEngine.UI;   // requires com.unity.ugui in Packages/manifest.json

public class LabSceneAutoSetup : Editor
{
    [MenuItem("Lab/Setup Lab 9 Scene")]
    static void SetupLab9Scene()
    {
        // ── Clear existing objects ─────────────────────────────────────────
        foreach (var go in Object.FindObjectsOfType<GameObject>())
            Object.DestroyImmediate(go);

        // ── Lighting ───────────────────────────────────────────────────────
        GameObject lightGO = new GameObject("Directional Light");
        Light light = lightGO.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightGO.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        // ── Ground plane ───────────────────────────────────────────────────
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.localScale = new Vector3(3f, 1f, 3f);
        SetColor(ground, new Color(0.3f, 0.5f, 0.3f));

        // ── Player ─────────────────────────────────────────────────────────
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 1f, 0f);
        SetColor(player, new Color(0.2f, 0.5f, 1f));

        // Remove default CapsuleCollider — CharacterController provides its own
        Object.DestroyImmediate(player.GetComponent<CapsuleCollider>());

        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;

        PlayerController pc = player.AddComponent<PlayerController>();
        pc.spawnPosition = new Vector3(0f, 1f, 0f);

        // ── Camera ─────────────────────────────────────────────────────────
        GameObject camGO = new GameObject("Main Camera");
        camGO.tag = "MainCamera";
        Camera cam = camGO.AddComponent<Camera>();
        cam.clearFlags = CameraClearFlags.Skybox;
        camGO.transform.position = new Vector3(0f, 4f, -7f);
        camGO.transform.LookAt(player.transform);
        camGO.AddComponent<AudioListener>();

        CameraFollow cf = camGO.AddComponent<CameraFollow>();
        cf.target = player.transform;
        cf.distance = 6f;
        cf.height = 3.2f;

        // ── Obstacles (4 rotating cubes) ────────────────────────────────────
        Vector3[] obsPos = {
            new Vector3( 5f, 0.75f,  5f),
            new Vector3(-5f, 0.75f,  5f),
            new Vector3( 5f, 0.75f, -5f),
            new Vector3(-5f, 0.75f, -5f),
        };
        Color[] obsColors = {
            new Color(0.8f, 0.2f, 0.2f),
            new Color(0.8f, 0.6f, 0.1f),
            new Color(0.5f, 0.2f, 0.8f),
            new Color(0.1f, 0.6f, 0.8f),
        };
        for (int i = 0; i < obsPos.Length; i++)
        {
            GameObject obs = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obs.name = "Obstacle_" + (i + 1);
            obs.transform.position = obsPos[i];
            obs.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
            SetColor(obs, obsColors[i]);
            obs.AddComponent<RotatingObject>().rotateSpeed = 30f + i * 10f;
        }

        // ── Collectibles (5 golden spheres) ─────────────────────────────────
        Vector3[] gemPos = {
            new Vector3( 3f, 0.5f,  0f),
            new Vector3(-3f, 0.5f,  0f),
            new Vector3( 0f, 0.5f,  4f),
            new Vector3( 0f, 0.5f, -4f),
            new Vector3( 4f, 0.5f, -4f),
        };
        Color gemColor = new Color(1f, 0.9f, 0.1f);
        for (int i = 0; i < gemPos.Length; i++)
        {
            GameObject gem = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            gem.name = "Collectible_" + (i + 1);
            gem.transform.position = gemPos[i];
            gem.transform.localScale = Vector3.one * 0.5f;
            SetColor(gem, gemColor);
            gem.GetComponent<SphereCollider>().isTrigger = true;
            gem.AddComponent<Collectible>();
        }

        // ── HUD Canvas ─────────────────────────────────────────────────────
        GameObject canvas = new GameObject("HUD Canvas");
        Canvas c = canvas.AddComponent<Canvas>();
        c.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.AddComponent<CanvasScaler>();
        canvas.AddComponent<GraphicRaycaster>();

        // Count label (top-left)
        Text countText = MakeText(canvas, "CollectibleCount",
            "Collected: 0 / 5", 28, Color.white, FontStyle.Bold,
            new Vector2(0f, 1f), new Vector2(0f, 1f),
            new Vector2(20f, -20f), new Vector2(300f, 50f));

        // Controls hint (bottom-left)
        MakeText(canvas, "ControlsHint",
            "WASD: Move  Space: Jump  R: Reset  Esc: Quit",
            18, new Color(1f, 1f, 1f, 0.75f), FontStyle.Normal,
            new Vector2(0f, 0f), new Vector2(0f, 0f),
            new Vector2(20f, 20f), new Vector2(520f, 40f));

        // Win label (centre, starts hidden)
        Text winText = MakeText(canvas, "WinText",
            "You Win! All Collectibles Gathered!",
            40, new Color(1f, 0.9f, 0.1f), FontStyle.Bold,
            new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
            new Vector2(0f, 0f), new Vector2(650f, 80f),
            TextAnchor.MiddleCenter);
        winText.gameObject.SetActive(false);

        // HUD controller
        GameObject hudGO = new GameObject("GameHUD");
        GameHUD hud = hudGO.AddComponent<GameHUD>();
        hud.collectibleCountText = countText;
        hud.winText = winText;
        hud.totalCollectibles = 5;

        // ── Done ───────────────────────────────────────────────────────────
        Debug.Log("[Lab 9] Scene built successfully! Press Play to start.");
        EditorUtility.DisplayDialog("Lab 9 Setup Complete",
            "Scene built!\n\nPress PLAY to run the interactive 3D scene.\n\n" +
            "Controls:\n  WASD - Move\n  Space - Jump\n  R - Reset\n  Esc - Quit",
            "OK");
    }

    // ── Helpers ──────────────────────────────────────────────────────────────
    static void SetColor(GameObject go, Color color)
    {
        Renderer r = go.GetComponent<Renderer>();
        if (r == null) return;
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = color;
        r.sharedMaterial = mat;
    }

    static Text MakeText(GameObject canvas, string name, string content,
        int fontSize, Color color, FontStyle style,
        Vector2 anchorMin, Vector2 anchorMax, Vector2 anchoredPos, Vector2 size,
        TextAnchor alignment = TextAnchor.UpperLeft)
    {
        GameObject go = new GameObject(name);
        go.transform.SetParent(canvas.transform, false);
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
#endif
