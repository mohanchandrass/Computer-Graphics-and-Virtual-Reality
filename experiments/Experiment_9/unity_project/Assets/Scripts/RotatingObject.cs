using UnityEngine;

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Continuously rotates a GameObject around the Y-axis (world space).
/// Attach to obstacle cubes or decorative objects.
/// </summary>
public class RotatingObject : MonoBehaviour
{
    [Tooltip("Degrees rotated per second around the Y axis.")]
    public float rotateSpeed = 45f;

    void Update()
    {
        transform.Rotate(Vector3.up * rotateSpeed * Time.deltaTime, Space.World);
    }
}

