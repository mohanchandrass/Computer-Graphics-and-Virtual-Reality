using UnityEngine;
using UnityEngine.UI;

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Singleton HUD controller. Tracks collected items and shows win state.
/// Attach to an empty GameObject in the scene; it will find the Canvas UI Text elements.
/// </summary>
public class GameHUD : MonoBehaviour
{
    // ---- Singleton ----
    public static GameHUD Instance { get; private set; }

    [Header("UI References")]
    public Text collectibleCountText;   // assign in Inspector or found automatically
    public Text winText;                // shows "You Win!" when all collected

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
            collectibleCountText.text = $"Collected: {_collected} / {totalCollectibles}";

        if (winText != null)
            winText.gameObject.SetActive(_collected >= totalCollectibles);
    }
}

