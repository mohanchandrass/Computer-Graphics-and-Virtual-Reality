using UnityEngine;

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Attach to a collectible gem. When the Player enters its trigger collider
/// the collectible is counted by GameHUD and this GameObject is destroyed.
/// </summary>
public class Collectible : MonoBehaviour
{
    [Header("Animation")]
    public float rotateSpeed = 75f;  // degrees per second (Y-axis spin)
    public float bobAmplitude = 0.25f;
    public float bobFrequency = 2f;

    private float _startY;
    private float _timeOffset;

    void Start()
    {
        _startY = transform.position.y;
        _timeOffset = Random.Range(0f, Mathf.PI * 2f); // randomise phase so gems don't sync
    }

    void Update()
    {
        // Continuous Y-axis rotation
        transform.Rotate(Vector3.up, rotateSpeed * Time.deltaTime, Space.World);

        // Harmonic vertical bobbing:  y(t) = y₀ + A·sin(ω·t + φ₀)
        float newY = _startY + bobAmplitude * Mathf.Sin(bobFrequency * Time.time + _timeOffset);
        transform.position = new Vector3(transform.position.x, newY, transform.position.z);
    }

    void OnTriggerEnter(Collider other)
    {
        if (!other.CompareTag("Player")) return;

        GameHUD.Instance?.AddCollectible();
        Destroy(gameObject);
    }
}

