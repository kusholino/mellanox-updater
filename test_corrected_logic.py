#!/usr/bin/env python3
"""
Test the corrected login filtering with the updated parser logic.
"""

def test_corrected_logic():
    """Test with corrected parser output."""
    
    # Sample playbook steps with CORRECTED parser output (send vs command)
    corrected_playbook = [
        ('wait', 'login:'),
        ('send', 'admin'),          # Now correctly parsed as 'send'
        ('wait', 'Password:'),
        ('send', 'qx4k^hDzNt'),     # Now correctly parsed as 'send'
        ('wait', 'PROMPT'),
        ('send', 'show diag'),      # This should be kept after login
        ('wait', 'PROMPT'),
        ('send', 'show configuration'),  # This should be kept
        ('pause', 10),
        ('wait', 'PROMPT')
    ]
    
    print("Corrected playbook steps (with fixed parser):")
    for i, (step_type, value) in enumerate(corrected_playbook, 1):
        print(f"  {i}. {step_type.upper()} {value}")
    
    # Apply the filtering logic
    filtered_playbook_steps = []
    login_keywords = ['login:', 'username:', 'user:', 'password:', 'admin', 'enable']
    common_login_cmds = ['admin', 'enable', 'login', 'su']
    in_login_sequence = True
    
    print("\nFiltering process (assuming already logged in):")
    for step_type, value in corrected_playbook:
        is_login_step = False
        
        if in_login_sequence:
            if step_type == 'wait':
                wait_value_lower = value.lower().strip()
                if any(keyword in wait_value_lower for keyword in login_keywords):
                    is_login_step = True
                elif wait_value_lower in ['prompt', '>', '#', '$']:
                    is_login_step = True
            elif step_type == 'send':  # Now this will match!
                send_value_lower = value.lower().strip()
                if any(keyword in send_value_lower for keyword in login_keywords):
                    is_login_step = True
                elif send_value_lower in common_login_cmds:
                    is_login_step = True
                elif len(value.strip()) < 20 and not any(cmd in value.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                    is_login_step = True
                    
                # If we see actual configuration commands, we're past login
                if any(cmd in value.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                    in_login_sequence = False
            elif step_type == 'command':  # This would be for actual commands
                in_login_sequence = False
                is_login_step = False
        
        if is_login_step:
            print(f"  ✓ SKIPPING: {step_type.upper()} {value}")
        else:
            print(f"  → KEEPING:  {step_type.upper()} {value}")
            filtered_playbook_steps.append((step_type, value))
    
    print(f"\nResult: Filtered from {len(corrected_playbook)} to {len(filtered_playbook_steps)} steps")
    print("\nSteps that will be executed:")
    for i, (step_type, value) in enumerate(filtered_playbook_steps, 1):
        print(f"  {i}. {step_type.upper()} {value}")
    
    # Check if problematic steps are now correctly filtered
    problematic_steps = ['admin']
    kept_values = [value for step_type, value in filtered_playbook_steps]
    
    success = True
    for problematic in problematic_steps:
        if problematic in kept_values:
            print(f"\n❌ FAILURE: '{problematic}' should have been skipped!")
            success = False
    
    if success:
        print(f"\n✅ SUCCESS: Login filtering now works correctly!")
    else:
        print(f"\n❌ FAILURE: Still has issues.")
    
    return success

if __name__ == '__main__':
    test_corrected_logic()
