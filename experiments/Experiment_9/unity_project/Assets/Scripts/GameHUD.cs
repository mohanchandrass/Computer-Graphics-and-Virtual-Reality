using UnityEngine;
using UnityEngine.UI;   // requires com.unity.ugui package in manifest.json

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Singleton HUD controller. Tracks collected items and shows win state.
/// Requires a Canvas with two Text children assigned in the Inspector,
/// OR let LabSceneAutoSetup create them automatically via the Lab menu.
/// </summary>
public class GameHUD : MonoBehaviour
{
    // ---- Singleton ----
    public static GameHUD Instance { get; private set; }

    [Header("UI References (assign in Inspector or set by LabSceneAutoSetup)")]
    public Text collectibleCountText;   // "Collected: X / 5"
    public Text winText;                // "You Win!" — hidden until all collected

    [Header("Settings")]
    public int totalCollectibles = 5;

    private int _collected = 0;

    void Awake()
    {
        if (Instance != null && Instance != this) { Destroy(gameObject); return; }
        Instance = this;
    }

    void Start()
    {
        _collected = 0;
        Refresh();
    }

    /// <summary>Call from Collectible.OnTriggerEnter to register a pickup.</summary>
    public void AddCollectible()
    {
        _collected = Mathf.Min(_collected + 1, totalCollectibles);
        Refresh();
    }

    /// <summary>Resets the counter (called when player presses R).</summary>
    public void ResetCollectibles()
    {
        _collected = 0;
        Refresh();
    }

    private void Refresh()
    {
        if (collectibleCountText != null)
            collectibleCountText.text = string.Format("Collected: {0} / {1}", _collected, totalCollectibles);

        if (winText != null)
            winText.gameObject.SetActive(_collected >= totalCollectibles);
    }
}
