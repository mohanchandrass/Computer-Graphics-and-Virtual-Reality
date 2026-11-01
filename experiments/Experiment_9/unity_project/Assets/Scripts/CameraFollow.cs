using UnityEngine;

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Smooth third-person camera that orbits behind and above the player.
/// Attach this to the Main Camera.
/// </summary>
public class CameraFollow : MonoBehaviour
{
    [Header("Target")]
    public Transform target;

    [Header("Offset")]
    public float distance = 6f;
    public float height = 3.2f;

    [Header("Smoothing")]
    [Range(0f, 1f)]
    public float positionLerpSpeed = 0.12f;

    void LateUpdate()
    {
        if (target == null) return;

        // Desired camera position: behind & above the player
        Vector3 desiredPos = target.position
                             - target.forward * distance
                             + Vector3.up * height;

        // Smoothly interpolate to desired position
        transform.position = Vector3.Lerp(transform.position, desiredPos, positionLerpSpeed);

        // Always look at a point slightly above the player's feet
        transform.LookAt(target.position + Vector3.up * 0.6f);
    }
}

