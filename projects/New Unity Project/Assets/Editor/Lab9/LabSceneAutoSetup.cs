// Editor-only scene builder for Experiment 9.
// Menu: Lab ▶ Setup Lab 9 Scene
// Run ONCE in an empty scene to build the full interactive 3D scene.
#if UNITY_EDITOR
using UnityEngine;
using UnityEditor;
using UnityEngine.UI;

public class LabSceneAutoSetup : Editor
{
    [MenuItem("Lab/Setup Lab 9 Scene")]
    static void SetupLab9Scene()
    {
        // ── Clear existing objects (except camera) ──────────────────────────
        foreach (var go in Object.FindObjectsOfType<GameObject>())
        {
            if (go.name != "Directional Light")   // keep default light if present
                Object.DestroyImmediate(go);
        }

        // ── Lighting ────────────────────────────────────────────────────────
        GameObject lightGO = new GameObject("Directional Light");
        Light light = lightGO.AddComponent<Light>();
        light.type = LightType.Directional;
        light.intensity = 1.2f;
        lightGO.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

        // ── Ground plane ────────────────────────────────────────────────────
        GameObject ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
        ground.name = "Ground";
        ground.transform.localScale = new Vector3(3f, 1f, 3f);
        SetColor(ground, new Color(0.3f, 0.5f, 0.3f));

        // ── Player ──────────────────────────────────────────────────────────
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 1f, 0f);
        SetColor(player, new Color(0.2f, 0.5f, 1f));

        // Remove default CapsuleCollider; CharacterController provides its own
        Object.DestroyImmediate(player.GetComponent<CapsuleCollider>());

        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;
        cc.center = new Vector3(0f, 0f, 0f);

        PlayerController pc = player.AddComponent<PlayerController>();
        pc.spawnPosition = new Vector3(0f, 1f, 0f);

        // ── Camera ──────────────────────────────────────────────────────────
        GameObject camGO = new GameObject("Main Camera");
        Camera cam = camGO.AddComponent<Camera>();
        cam.tag = "MainCamera";
        cam.clearFlags = CameraClearFlags.Skybox;
        camGO.transform.position = new Vector3(0f, 4f, -7f);
        camGO.transform.LookAt(player.transform);

        CameraFollow cf = camGO.AddComponent<CameraFollow>();
        cf.target = player.transform;
        cf.distance = 6f;
        cf.height = 3.2f;

        AudioListener al = camGO.AddComponent<AudioListener>();

        // ── Obstacles (4 static cubes) ──────────────────────────────────────
        Vector3[] obstaclePositions = {
            new Vector3( 5f, 0.75f,  5f),
            new Vector3(-5f, 0.75f,  5f),
            new Vector3( 5f, 0.75f, -5f),
            new Vector3(-5f, 0.75f, -5f),
        };
        Color[] obstacleColors = {
            new Color(0.8f, 0.2f, 0.2f),
            new Color(0.8f, 0.6f, 0.1f),
            new Color(0.5f, 0.2f, 0.8f),
            new Color(0.1f, 0.6f, 0.8f),
        };
        for (int i = 0; i < obstaclePositions.Length; i++)
        {
            GameObject obs = GameObject.CreatePrimitive(PrimitiveType.Cube);
            obs.name = $"Obstacle_{i + 1}";
            obs.transform.position = obstaclePositions[i];
            obs.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);
            SetColor(obs, obstacleColors[i]);
            obs.AddComponent<RotatingObject>().rotateSpeed = 30f + i * 10f;
        }

        // ── Collectibles (5 spheres) ─────────────────────────────────────────
        Vector3[] gemPositions = {
            new Vector3( 3f, 0.5f,  0f),
            new Vector3(-3f, 0.5f,  0f),
            new Vector3( 0f, 0.5f,  4f),
            new Vector3( 0f, 0.5f, -4f),
            new Vector3( 4f, 0.5f, -4f),
        };
        Color gemColor = new Color(1f, 0.9f, 0.1f);  // golden-yellow
        for (int i = 0; i < gemPositions.Length; i++)
        {
            GameObject gem = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            gem.name = $"Collectible_{i + 1}";
            gem.transform.position = gemPositions[i];
            gem.transform.localScale = Vector3.one * 0.5f;
            SetColor(gem, gemColor);

            // Make collider a trigger
            gem.GetComponent<SphereCollider>().isTrigger = true;
            gem.AddComponent<Collectible>();
        }

        // ── HUD Canvas ──────────────────────────────────────────────────────
        GameObject canvas = new GameObject("HUD Canvas");
        Canvas c = canvas.AddComponent<Canvas>();
        c.renderMode = RenderMode.ScreenSpaceOverlay;
        canvas.AddComponent<CanvasScaler>();
        canvas.AddComponent<GraphicRaycaster>();

        // Count label
        GameObject countGO = new GameObject("CollectibleCount");
        countGO.transform.SetParent(canvas.transform, false);
        Text countText = countGO.AddComponent<Text>();
        countText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        countText.text = "Collected: 0 / 5";
        countText.fontSize = 28;
        countText.color = Color.white;
        countText.fontStyle = FontStyle.Bold;
        RectTransform countRT = countGO.GetComponent<RectTransform>();
        countRT.anchorMin = new Vector2(0f, 1f);
        countRT.anchorMax = new Vector2(0f, 1f);
        countRT.pivot     = new Vector2(0f, 1f);
        countRT.anchoredPosition = new Vector2(20f, -20f);
        countRT.sizeDelta = new Vector2(300f, 50f);

        // Controls label
        GameObject ctrlGO = new GameObject("ControlsHint");
        ctrlGO.transform.SetParent(canvas.transform, false);
        Text ctrlText = ctrlGO.AddComponent<Text>();
        ctrlText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        ctrlText.text = "WASD: Move  Space: Jump  R: Reset  Esc: Quit";
        ctrlText.fontSize = 18;
        ctrlText.color = new Color(1f, 1f, 1f, 0.75f);
        RectTransform ctrlRT = ctrlGO.GetComponent<RectTransform>();
        ctrlRT.anchorMin = new Vector2(0f, 0f);
        ctrlRT.anchorMax = new Vector2(0f, 0f);
        ctrlRT.pivot     = new Vector2(0f, 0f);
        ctrlRT.anchoredPosition = new Vector2(20f, 20f);
        ctrlRT.sizeDelta = new Vector2(500f, 40f);

        // Win label
        GameObject winGO = new GameObject("WinText");
        winGO.transform.SetParent(canvas.transform, false);
        Text winText = winGO.AddComponent<Text>();
        winText.font = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
        winText.text = "🏆 You Win! All Collectibles Gathered!";
        winText.fontSize = 40;
        winText.color = new Color(1f, 0.9f, 0.1f);
        winText.fontStyle = FontStyle.Bold;
        winText.alignment = TextAnchor.MiddleCenter;
        RectTransform winRT = winGO.GetComponent<RectTransform>();
        winRT.anchorMin = new Vector2(0.5f, 0.5f);
        winRT.anchorMax = new Vector2(0.5f, 0.5f);
        winRT.pivot     = new Vector2(0.5f, 0.5f);
        winRT.anchoredPosition = Vector2.zero;
        winRT.sizeDelta = new Vector2(600f, 80f);
        winGO.SetActive(false);

        // HUD controller
        GameObject hudController = new GameObject("GameHUD");
        GameHUD hud = hudController.AddComponent<GameHUD>();
        hud.collectibleCountText = countText;
        hud.winText = winText;
        hud.totalCollectibles = 5;

        // ── Finish ──────────────────────────────────────────────────────────
        Debug.Log("[Lab 9] Scene built successfully! Press Play to start.");
        EditorUtility.DisplayDialog("Lab 9 Setup Complete",
            "Scene built!\n\nPress ▶ Play to run the interactive 3D scene.\n\n" +
            "Controls:\n  WASD – Move\n  Space – Jump\n  R – Reset\n  Esc – Quit",
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
}
#endif
