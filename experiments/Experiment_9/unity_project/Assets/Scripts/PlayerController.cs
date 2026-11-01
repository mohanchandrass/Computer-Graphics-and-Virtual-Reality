using UnityEngine;

/// <summary>
/// Experiment 9 – Simple Interactive 3D Scene
/// Player movement via explicit key checks (no dependency on Input Manager axis names).
/// Controls: WASD / Arrow keys to move & turn, Space to jump, R to reset, Esc to quit.
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
    public Vector3 spawnPosition = new Vector3(0f, 1f, 0f);

    private CharacterController _cc;
    private float _verticalVelocity = 0f;

    void Awake()
    {
        _cc = GetComponent<CharacterController>();
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
            transform.rotation = Quaternion.identity;
            _verticalVelocity = 0f;
            GameHUD.Instance?.ResetCollectibles();
        }

        // --- Turn (A/D or Left/Right arrow) ---
        float turnDir = 0f;
        if (Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow))  turnDir = -1f;
        if (Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow)) turnDir =  1f;
        transform.Rotate(0f, turnDir * turnSpeed * Time.deltaTime, 0f);

        // --- Move forward/back (W/S or Up/Down arrow) ---
        float forwardDir = 0f;
        if (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow))   forwardDir =  1f;
        if (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow)) forwardDir = -1f;

        // --- Jump / Gravity ---
        if (_cc.isGrounded)
        {
            _verticalVelocity = -1f; // small constant to keep grounded
            if (Input.GetKeyDown(KeyCode.Space))
                _verticalVelocity = jumpSpeed;
        }
        else
        {
            _verticalVelocity -= gravity * Time.deltaTime;
        }

        // --- Apply movement ---
        Vector3 move = transform.forward * forwardDir * moveSpeed;
        move.y = _verticalVelocity;
        _cc.Move(move * Time.deltaTime);
    }
}
