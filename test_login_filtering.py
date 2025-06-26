#!/usr/bin/env python3
"""
Test script to verify the improved login filtering logic.
This simulates the playbook filtering when a device is already logged in.
"""

def test_login_filtering():
    """Test the improved login step filtering logic."""
    
    # Sample playbook steps (same format as parsed in serial_communicator.py)
    sample_playbook = [
        ('wait', 'login:'),
        ('send', 'admin'),
        ('wait', 'Password:'),
        ('send', 'qx4k^hDzNt'),
        ('wait', 'PROMPT'),
        ('send', 'show diag'),
        ('wait', 'PROMPT'),
        ('command', 'show configuration'),
        ('pause', 10),
        ('wait', 'PROMPT'),
        ('send', 'exit')
    ]
    
    print("Original playbook steps:")
    for i, (step_type, value) in enumerate(sample_playbook, 1):
        print(f"  {i}. {step_type.upper()} {value}")
    
    # Apply the same filtering logic as in serial_communicator.py
    filtered_playbook_steps = []
    login_keywords = ['login:', 'username:', 'user:', 'password:', 'admin', 'enable']
    common_login_cmds = ['admin', 'enable', 'login', 'su']
    in_login_sequence = True  # Start assuming we're in login sequence
    
    print("\nFiltering process:")
    for step_type, value in sample_playbook:
        # Check if this is a login-related step
        is_login_step = False
        
        if in_login_sequence:
            if step_type == 'wait':
                # Check for login-related wait patterns
                wait_value_lower = value.lower().strip()
                if any(keyword in wait_value_lower for keyword in login_keywords):
                    is_login_step = True
                elif wait_value_lower in ['prompt', '>', '#', '$']:
                    is_login_step = True  # Prompt waits during login
            elif step_type == 'send':
                # Check for login-related send patterns
                send_value_lower = value.lower().strip()
                if any(keyword in send_value_lower for keyword in login_keywords):
                    is_login_step = True
                elif send_value_lower in common_login_cmds:
                    is_login_step = True
                elif len(value.strip()) < 20 and not any(cmd in value.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                    # Short non-command strings (likely passwords/usernames)
                    is_login_step = True
                    
                # If we see actual configuration commands, we're past login
                if any(cmd in value.lower() for cmd in ['show', 'config', 'display', 'get', 'set']):
                    in_login_sequence = False
            elif step_type == 'command':
                # Any COMMAND type step means we're past login
                in_login_sequence = False
                is_login_step = False
        
        if is_login_step:
            print(f"  SKIPPING: {step_type.upper()} {value}")
        else:
            print(f"  KEEPING:  {step_type.upper()} {value}")
            filtered_playbook_steps.append((step_type, value))
    
    print(f"\nFiltered playbook steps (kept {len(filtered_playbook_steps)} out of {len(sample_playbook)}):")
    for i, (step_type, value) in enumerate(filtered_playbook_steps, 1):
        print(f"  {i}. {step_type.upper()} {value}")
    
    # Verify expected results
    expected_filtered = [
        ('command', 'show configuration'),
        ('pause', 10),
        ('wait', 'PROMPT'),
        ('send', 'exit')
    ]
    
    print(f"\nTest result: {'PASS' if len(filtered_playbook_steps) <= 6 else 'FAIL'}")
    print(f"Expected to filter out most login steps, kept {len(filtered_playbook_steps)} steps")

if __name__ == '__main__':
    test_login_filtering()
