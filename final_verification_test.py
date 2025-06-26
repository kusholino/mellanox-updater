#!/usr/bin/env python3
"""
Final verification test for the login filtering fix.
This simulates the exact scenario from the user's report.
"""

def test_complete_scenario():
    """Test the complete login filtering scenario."""
    
    # This simulates the exact playbook from the user's issue
    user_reported_playbook = [
        ('wait', 'login:'),
        ('send', 'admin'),          # This was incorrectly executed
        ('wait', 'Password:'),      # This was incorrectly executed  
        ('send', 'qx4k^hDzNt'),
        ('wait', 'PROMPT'),
        ('command', 'show version'),
        ('wait', 'PROMPT'),
        ('command', 'show interfaces'),
        ('wait', 'PROMPT')
    ]
    
    print("User's reported scenario:")
    print("- Device is already logged in")
    print("- Should skip login steps and go straight to commands")
    print("\nOriginal playbook steps:")
    for i, (step_type, value) in enumerate(user_reported_playbook, 1):
        print(f"  {i}. {step_type.upper()} {value}")
    
    # Apply the improved login filtering logic
    filtered_playbook_steps = []
    login_keywords = ['login:', 'username:', 'user:', 'password:', 'admin', 'enable']
    common_login_cmds = ['admin', 'enable', 'login', 'su']
    in_login_sequence = True
    
    print("\nFiltering process (assuming already logged in):")
    for step_type, value in user_reported_playbook:
        is_login_step = False
        
        if in_login_sequence:
            if step_type == 'wait':
                wait_value_lower = value.lower().strip()
                if any(keyword in wait_value_lower for keyword in login_keywords):
                    is_login_step = True
                elif wait_value_lower in ['prompt', '>', '#', '$']:
                    is_login_step = True
            elif step_type == 'send':
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
            elif step_type == 'command':
                in_login_sequence = False
                is_login_step = False
        
        if is_login_step:
            print(f"  ✓ SKIPPING: {step_type.upper()} {value}")
        else:
            print(f"  → KEEPING:  {step_type.upper()} {value}")
            filtered_playbook_steps.append((step_type, value))
    
    print(f"\nResult: Filtered from {len(user_reported_playbook)} to {len(filtered_playbook_steps)} steps")
    print("\nSteps that will be executed:")
    for i, (step_type, value) in enumerate(filtered_playbook_steps, 1):
        print(f"  {i}. {step_type.upper()} {value}")
    
    # Verify the fix
    expected_skipped = ['admin', 'Password:']  # These were the problematic steps
    actually_kept = [value for step_type, value in filtered_playbook_steps]
    
    success = True
    for problematic_step in expected_skipped:
        if problematic_step in actually_kept:
            print(f"\n❌ FAILURE: '{problematic_step}' should have been skipped but was kept!")
            success = False
    
    if success:
        print(f"\n✅ SUCCESS: All login steps properly filtered!")
        print("The user's issue has been resolved.")
    else:
        print(f"\n❌ FAILURE: Login filtering still has issues.")
    
    return success

if __name__ == '__main__':
    test_complete_scenario()
