using UnityEngine;

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Handles player movement, turning, jumping, and reset via CharacterController.
/// Controls: WASD / Arrow keys to move, Space to jump, R to reset, Esc to quit.
/// </summary>
[RequireComponent(typeof(CharacterController))]
public class PlayerController : MonoBehaviour
{
    [Header("Movement")]
    public float moveSpeed = 6f;
    public float turnSpeed = 120f;

    [Header("Jump / Gravity")]
    public float jumpSpeed = 8.5f;
    public float gravity = 24f;

    [Header("Reset")]
    public Vector3 spawnPosition = new Vector3(0f, 0.5f, 0f);

    // ----- private state -----
    private CharacterController _cc;
    private float _verticalVelocity = 0f;

    void Awake()
    {
        _cc = GetComponent<CharacterController>();
        transform.position = spawnPosition;
    }

    void Update()
    {
        // --- Quit ---
        if (Input.GetKeyDown(KeyCode.Escape))
        {
#if UNITY_EDITOR
            UnityEditor.EditorApplication.isPlaying = false;
#else
            Application.Quit();
#endif
        }

        // --- Reset ---
        if (Input.GetKeyDown(KeyCode.R))
        {
            transform.position = spawnPosition;
            _verticalVelocity = 0f;
            transform.rotation = Quaternion.identity;
            GameHUD.Instance?.ResetCollectibles();
        }

        // --- Horizontal movement & turning ---
        float turn = Input.GetAxis("Horizontal") * turnSpeed * Time.deltaTime;
        transform.Rotate(0f, turn, 0f);

        float forward = Input.GetAxis("Vertical") * moveSpeed;

        // --- Gravity & Jump ---
        if (_cc.isGrounded)
        {
            _verticalVelocity = -0.5f; // small downward force to stay grounded

            if (Input.GetKeyDown(KeyCode.Space))
                _verticalVelocity = jumpSpeed;
        }
        else
        {
            _verticalVelocity -= gravity * Time.deltaTime;
        }

        // Build motion vector in world space
        Vector3 motion = transform.forward * forward;
        motion.y = _verticalVelocity;
        motion *= Time.deltaTime;

        _cc.Move(motion);
    }
}

