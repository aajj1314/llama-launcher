# User Friendliness Test Plan

## Project Overview
**Project**: Llama Launcher v4.0
**Location**: `/workspace/new_llama_launcher/`
**Focus**: Testing user-friendliness, specifically parameter persistence in web UI

## Test Objectives

1. **Parameter Persistence Test** - Verify that parameters do not jump back when modified in web UI
2. **Configuration Management Test** - Test configuration save and load functionality
3. **User Interface Test** - Evaluate overall user experience
4. **Process Management Test** - Test model startup/stop functionality
5. **Log Management Test** - Verify logs are properly captured and displayed

## Test Environment Setup

### 1. Install Dependencies
```bash
cd /workspace/new_llama_launcher
pip install -r requirements.txt
```

### 2. Start the Service
```bash
python main.py
```

### 3. Access Web Interface
- Open browser at `http://localhost:8000`
- Wait for initial loading and status check

## Test Cases

### Test Case 1: Parameter Persistence Test

**Steps**:
1. Navigate to the web interface
2. Modify the following parameters WITHOUT clicking "Save Config":
   - Run Mode (change to different option)
   - Context Size (select different value)
   - GPU Layers (ngl) (select different value)
   - Port (change to different number)
3. Wait for 10 seconds to see if values reset
4. Refresh the page and check if values persist
5. Verify that values only change when explicitly saved

**Expected Result**:
- Parameters should NOT automatically reset
- Values should remain as modified until "Save Config" is clicked
- After refresh, values should return to last saved state

### Test Case 2: Configuration Save Test

**Steps**:
1. Modify multiple parameters
2. Click "Save Config" button
3. Verify success message appears
4. Refresh the page
5. Check if parameters remain as saved
6. Restart the service and check if parameters load correctly

**Expected Result**:
- Configuration should be saved successfully
- Parameters should persist after page refresh
- Parameters should load correctly after service restart

### Test Case 3: Model Selection Test

**Steps**:
1. Set llama.cpp path (use a test directory if available)
2. Click "Update Path"
3. Check if model scan completes
4. Select a model from the list
5. Verify selected model remains selected
6. Modify other parameters and check if model selection is preserved

**Expected Result**:
- Model selection should persist
- Model selection should not be affected by other parameter changes

### Test Case 4: Process Management Test

**Steps**:
1. Select a model (if available)
2. Configure run parameters
3. Click "Start" button
4. Verify process starts successfully
5. Check log output in web interface
6. Click "Stop" button
7. Verify process stops successfully

**Expected Result**:
- Process should start and stop cleanly
- Logs should appear in web interface (not in terminal)
- Terminal should not be spammed with output

### Test Case 5: Error Handling Test

**Steps**:
1. Try to start without selecting a model
2. Try to update path with invalid directory
3. Try to start with invalid parameters
4. Check error messages and UI feedback

**Expected Result**:
- Clear error messages should be displayed
- UI should remain responsive
- No crashes or unexpected behavior

## Test Verification

### Key Metrics to Verify

1. **✅ Parameter Persistence** - No automatic reset of user inputs
2. **✅ Configuration Persistence** - Settings saved between sessions
3. **✅ User Feedback** - Clear success/error messages
4. **✅ Log Management** - No terminal刷屏 (spamming)
5. **✅ Responsive UI** - Smooth interactions, no lag

### Success Criteria

The project will be considered "user-friendly" if:
- All parameters remain as modified until explicitly saved
- No automatic reset of user inputs
- Logs are properly managed and displayed in web UI
- Error messages are clear and helpful
- Overall UI is intuitive and responsive

## Test Cleanup

1. Stop the running service (Ctrl+C in terminal)
2. Check configuration file at `~/.llama_launcher_v4/config.json`
3. Verify no temporary files were created

## Risk Assessment

### Potential Issues
1. **No llama.cpp installation** - May not be able to test actual model startup
2. **No models available** - May not be able to test model selection
3. **Port conflicts** - May need to use different port

### Mitigation
1. Use dummy paths if llama.cpp is not available
2. Test with empty model directory to verify error handling
3. Use `--port` parameter to specify alternative port if needed
