using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Experiment 9 — Auto-Bootstrap
/// Automatically builds the entire Lab 9 scene at runtime when you press Play.
/// No setup menu needed — just open the project and press Play.
/// Uses [RuntimeInitializeOnLoadMethod] so it fires even in an empty scene.
/// </summary>
public class Lab9Bootstrap
{
    [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
    static void Bootstrap()
    {
        Debug.Log("[Lab 9] Auto-bootstrapping scene...");

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
        ApplyColor(ground, new Color(0.25f, 0.45f, 0.25f));

        // ── Player capsule ─────────────────────────────────────────────────
        GameObject player = GameObject.CreatePrimitive(PrimitiveType.Capsule);
        player.name = "Player";
        player.tag = "Player";
        player.transform.position = new Vector3(0f, 1f, 0f);
        ApplyColor(player, new Color(0.2f, 0.5f, 1f));

        // CharacterController replaces the CapsuleCollider
        Object.Destroy(player.GetComponent<CapsuleCollider>());
        CharacterController cc = player.AddComponent<CharacterController>();
        cc.height = 2f;
        cc.radius = 0.5f;

        PlayerController pc = player.AddComponent<PlayerController>();
        pc.spawnPosition = new Vector3(0f, 1f, 0f);

        // ── Camera ─────────────────────────────────────────────────────────
        // Check if a Main Camera already exists
        GameObject camGO = GameObject.FindWithTag("MainCamera");
        if (camGO == null)
        {
            camGO = new GameObject("Main Camera");
            camGO.tag = "MainCamera";
            camGO.AddComponent<Camera>();
            camGO.AddComponent<AudioListener>();
        }
        camGO.transform.position = new Vector3(0f, 4f, -7f);
        camGO.transform.LookAt(player.transform);

        CameraFollow cf = camGO.GetComponent<CameraFollow>();
        if (cf == null) cf = camGO.AddComponent<CameraFollow>();
        cf.target = player.transform;
        cf.distance = 6f;
        cf.height = 3.2f;
        cf.positionLerpSpeed = 0.12f;

        // ── Obstacles ──────────────────────────────────────────────────────
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
            ApplyColor(obs, obsColors[i]);
            obs.AddComponent<RotatingObject>().rotateSpeed = 30f + i * 10f;
        }

        // ── Collectibles ───────────────────────────────────────────────────
        Vector3[] gemPos = {
            new Vector3( 3f, 0.5f,  0f),
            new Vector3(-3f, 0.5f,  0f),
            new Vector3( 0f, 0.5f,  4f),
            new Vector3( 0f, 0.5f, -4f),
            new Vector3( 4f, 0.5f, -4f),
        };
        for (int i = 0; i < gemPos.Length; i++)
        {
            GameObject gem = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            gem.name = "Collectible_" + (i + 1);
            gem.transform.position = gemPos[i];
            gem.transform.localScale = Vector3.one * 0.5f;
            ApplyColor(gem, new Color(1f, 0.85f, 0.1f));
            gem.GetComponent<SphereCollider>().isTrigger = true;
            gem.AddComponent<Collectible>();
        }

        // ── HUD Canvas ─────────────────────────────────────────────────────
        GameObject canvasGO = new GameObject("HUD Canvas");
        Canvas canvas = canvasGO.AddComponent<Canvas>();
        canvas.renderMode = RenderMode.ScreenSpaceOverlay;
        canvasGO.AddComponent<CanvasScaler>();
        canvasGO.AddComponent<GraphicRaycaster>();

        Text countText = MakeText(canvasGO, "CollectibleCount",
            "Collected: 0 / 5", 30, Color.white, FontStyle.Bold,
            new Vector2(0f, 1f), new Vector2(0f, 1f),
            new Vector2(20f, -20f), new Vector2(320f, 55f));

        MakeText(canvasGO, "Controls",
            "WASD: Move   Space: Jump   R: Reset   Esc: Quit",
            20, new Color(1f, 1f, 1f, 0.75f), FontStyle.Normal,
            new Vector2(0f, 0f), new Vector2(0f, 0f),
            new Vector2(20f, 20f), new Vector2(540f, 40f));

        Text winText = MakeText(canvasGO, "WinText",
            "You Win! All Collectibles Gathered!",
            42, new Color(1f, 0.9f, 0.1f), FontStyle.Bold,
            new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f),
            new Vector2(0f, 0f), new Vector2(660f, 80f),
            TextAnchor.MiddleCenter);
        winText.gameObject.SetActive(false);

        // ── GameHUD controller ─────────────────────────────────────────────
        GameObject hudGO = new GameObject("GameHUD");
        GameHUD hud = hudGO.AddComponent<GameHUD>();
        hud.collectibleCountText = countText;
        hud.winText = winText;
        hud.totalCollectibles = 5;

        Debug.Log("[Lab 9] Scene ready! Use WASD to move, Space to jump, R to reset.");
    }

    // ── Static helpers ─────────────────────────────────────────────────────
    static void ApplyColor(GameObject go, Color color)
    {
        Renderer r = go.GetComponent<Renderer>();
        if (r == null) return;
        Material mat = new Material(Shader.Find("Standard"));
        mat.color = color;
        r.material = mat;
    }

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
