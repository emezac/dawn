# Dawn Framework Error Codes Reference

This document provides a comprehensive reference for all error codes used in the Dawn framework, including standardized error messages and recommended solutions.

## Error Code Format

Error codes in the Dawn framework follow a standardized format:

```
<CATEGORY>_<DESCRIPTION>_<NUMBER>
```

For example: `VALIDATION_MISSING_FIELD_101`

## Validation Errors (100-199)

### VALIDATION_MISSING_FIELD_101

**Message Template:**  
"Required field '{field_name}' is missing"

**Common Causes:**
- A required parameter was not provided in a tool's input
- A required configuration setting is missing
- A required field is absent in a request payload

**Recommended Fix:**
- Check the tool's documentation for required parameters
- Add the missing field to your input data
- Ensure all required configuration settings are present

### VALIDATION_INVALID_TYPE_102

**Message Template:**  
"Invalid type for field '{field_name}': expected {expected_type}, received {received_type}"

**Common Causes:**
- The wrong data type was provided for a field
- A string was provided where a number was expected (or vice versa)
- A primitive value was provided where an object was expected

**Recommended Fix:**
- Convert the value to the expected type
- Check the tool's documentation for the correct parameter types
- Use appropriate type conversion functions if necessary

### VALIDATION_INVALID_FORMAT_103

**Message Template:**  
"Invalid format for field '{field_name}': {reason}"

**Common Causes:**
- A string doesn't match the expected pattern (e.g., email, URL, date)
- A JSON string is malformed
- An ID has the wrong format

**Recommended Fix:**
- Ensure the value matches the expected format
- Check the tool's documentation for format requirements
- Use proper formatting functions or validation before submitting

### VALIDATION_INVALID_VALUE_104

**Message Template:**  
"Invalid value for field '{field_name}': {reason}"

**Common Causes:**
- A value is outside the allowed range
- A value is not in the list of allowed values
- A value violates business rules or constraints

**Recommended Fix:**
- Provide a value within the allowed range or from the allowed set
- Check the documentation for value constraints
- Review business rules for the specific field

### VALIDATION_MISSING_DEPENDENCY_105

**Message Template:**  
"Field '{field_name}' requires '{dependency_field}' to be present"

**Common Causes:**
- A field that depends on another field was provided, but the dependency was not
- Incomplete configuration where related settings are missing
- Required related resources are not specified

**Recommended Fix:**
- Provide both the field and its dependency
- Check documentation for required field combinations
- Ensure all related configuration settings are present

## Execution Errors (200-299)

### EXECUTION_TASK_FAILED_201

**Message Template:**  
"Task '{task_id}' failed: {reason}"

**Common Causes:**
- An error occurred during task execution
- A task exceeded maximum allowed time
- A task's dependencies failed

**Recommended Fix:**
- Check the task logs for more details
- Verify that all task dependencies are working
- Review task settings and configuration

### EXECUTION_TOOL_FAILED_202

**Message Template:**  
"Tool '{tool_name}' execution failed: {reason}"

**Common Causes:**
- The tool encountered an error during execution
- The tool's backend service is unavailable
- The tool received valid but unprocessable input

**Recommended Fix:**
- Check the error message for specific details
- Verify the tool's dependencies and services are available
- Review the input data for potential issues

### EXECUTION_TIMEOUT_203

**Message Template:**  
"Operation timed out after {timeout} seconds"

**Common Causes:**
- The operation took longer than the allowed time
- A backend service is slow or unresponsive
- The operation involves too much data

**Recommended Fix:**
- Try again with a smaller dataset
- Increase the timeout if possible
- Check backend services for performance issues

### EXECUTION_INTERRUPTED_204

**Message Template:**  
"Operation was interrupted: {reason}"

**Common Causes:**
- The operation was manually cancelled
- The system was shut down during execution
- A signal interrupted the process

**Recommended Fix:**
- Restart the operation if needed
- Check system logs for interruption causes
- Consider implementing resumable operations

### EXECUTION_MAX_RETRIES_205

**Message Template:**  
"Maximum retries ({max_retries}) exceeded for '{resource_name}'"

**Common Causes:**
- A transient error persisted beyond retry limits
- A service is consistently unavailable
- There's a permanent error that won't be resolved by retrying

**Recommended Fix:**
- Check the underlying error messages
- Verify service health and availability
- Consider increasing max retries or implementing backoff

## Authentication Errors (300-399)

### AUTH_MISSING_CREDENTIALS_301

**Message Template:**  
"Missing credentials for '{service_name}'"

**Common Causes:**
- API key or token not provided
- Environment variables not set
- Configuration file missing credentials

**Recommended Fix:**
- Add the required credentials to your request
- Set the necessary environment variables
- Update configuration with proper credentials

### AUTH_INVALID_CREDENTIALS_302

**Message Template:**  
"Invalid credentials for '{service_name}'"

**Common Causes:**
- API key or token is incorrect
- Credentials have been revoked
- Using credentials for the wrong environment

**Recommended Fix:**
- Verify your credentials are correct
- Generate new credentials if necessary
- Check you're using the right credentials for the environment

### AUTH_EXPIRED_CREDENTIALS_303

**Message Template:**  
"Expired credentials for '{service_name}'"

**Common Causes:**
- Token has expired
- API key has reached its expiration date
- Temporary credentials have timed out

**Recommended Fix:**
- Refresh your token
- Generate new credentials
- Implement automatic token refresh in your application

### AUTH_INSUFFICIENT_PERMISSIONS_304

**Message Template:**  
"Insufficient permissions to access '{resource_name}'"

**Common Causes:**
- The authenticated user lacks the required permissions
- Trying to access a restricted resource
- Role-based access control (RBAC) preventing access

**Recommended Fix:**
- Request elevated permissions
- Use credentials with appropriate access levels
- Check permission requirements in documentation

## Connection Errors (400-499)

### CONNECTION_FAILED_401

**Message Template:**  
"Failed to connect to '{service_name}': {reason}"

**Common Causes:**
- Service is unreachable
- Network issues
- DNS resolution problems

**Recommended Fix:**
- Check network connectivity
- Verify the service URL is correct
- Check if the service is running

### CONNECTION_TIMEOUT_402

**Message Template:**  
"Connection to '{service_name}' timed out after {timeout} seconds"

**Common Causes:**
- Service is slow to respond
- Network latency
- Service is overloaded

**Recommended Fix:**
- Increase connection timeout
- Try again later
- Check service health metrics

### CONNECTION_RATE_LIMIT_403

**Message Template:**  
"Rate limit exceeded for '{service_name}'. Try again in {retry_after} seconds"

**Common Causes:**
- Too many requests in a short time period
- API quota exceeded
- Throttling by service provider

**Recommended Fix:**
- Implement backoff and rate limiting in your code
- Wait for the specified retry period
- Consider upgrading your service tier

### CONNECTION_API_ERROR_404

**Message Template:**  
"API error from '{service_name}': {reason}"

**Common Causes:**
- The API returned an error response
- Remote service encountered an internal error
- Invalid API request format

**Recommended Fix:**
- Check the detailed error message
- Consult the API documentation
- Verify your request format

## Resource Errors (500-599)

### RESOURCE_NOT_FOUND_501

**Message Template:**  
"Resource '{resource_type}' with ID '{resource_id}' not found"

**Common Causes:**
- The resource doesn't exist
- The resource was deleted
- Using the wrong resource identifier

**Recommended Fix:**
- Verify the resource ID is correct
- Check if the resource was deleted
- Create the resource if appropriate

### RESOURCE_ALREADY_EXISTS_502

**Message Template:**  
"Resource '{resource_type}' with ID '{resource_id}' already exists"

**Common Causes:**
- Trying to create a resource that already exists
- Duplicate resource ID
- Race condition in resource creation

**Recommended Fix:**
- Use a different resource ID
- Update the existing resource instead
- Implement idempotent operations

### RESOURCE_ACCESS_DENIED_503

**Message Template:**  
"Access denied to resource '{resource_type}' with ID '{resource_id}'"

**Common Causes:**
- The user doesn't have permission to access the resource
- The resource is owned by another user
- The resource has specific access controls

**Recommended Fix:**
- Request access to the resource
- Use a different resource that you have access to
- Check access control settings

### RESOURCE_UNAVAILABLE_504

**Message Template:**  
"Resource '{resource_type}' is currently unavailable: {reason}"

**Common Causes:**
- The resource is temporarily unavailable
- The resource is being modified
- The resource is locked by another process

**Recommended Fix:**
- Try again later
- Check if another process has a lock on the resource
- Wait for the resource to become available

## Framework Errors (600-699)

### FRAMEWORK_INITIALIZATION_ERROR_601

**Message Template:**  
"Framework initialization error: {reason}"

**Common Causes:**
- Missing required components or services
- Configuration errors
- Incompatible versions of components

**Recommended Fix:**
- Check framework requirements
- Verify configuration settings
- Ensure all components are compatible

### FRAMEWORK_CONFIGURATION_ERROR_602

**Message Template:**  
"Configuration error: {reason}"

**Common Causes:**
- Invalid configuration values
- Missing required configuration
- Configuration file format error

**Recommended Fix:**
- Review configuration documentation
- Provide all required configuration values
- Check configuration file format

### FRAMEWORK_WORKFLOW_ERROR_603

**Message Template:**  
"Workflow error in '{workflow_id}': {reason}"

**Common Causes:**
- Workflow definition is invalid
- Tasks in the workflow failed
- Workflow dependencies are unavailable

**Recommended Fix:**
- Check workflow logs for detailed errors
- Verify all tasks in the workflow
- Ensure workflow dependencies are available

### FRAMEWORK_TASK_ERROR_604

**Message Template:**  
"Task error in '{task_id}': {reason}"

**Common Causes:**
- Task implementation has an error
- Task inputs are invalid
- Task dependencies failed

**Recommended Fix:**
- Check the task implementation
- Verify task inputs are valid
- Ensure all task dependencies succeeded

### FRAMEWORK_ENGINE_ERROR_605

**Message Template:**  
"Engine error: {reason}"

**Common Causes:**
- The workflow engine encountered an internal error
- Resource limitations
- State management failures

**Recommended Fix:**
- Check logs for detailed error information
- Verify system resource availability
- Report the issue to framework maintainers

## Plugin Errors (700-799)

### PLUGIN_LOADING_ERROR_701

**Message Template:**  
"Error loading plugin '{plugin_name}': {reason}"

**Common Causes:**
- Plugin file is missing
- Plugin is incompatible with the current framework version
- Plugin has unmet dependencies

**Recommended Fix:**
- Verify the plugin file exists
- Check plugin compatibility
- Install required dependencies

### PLUGIN_EXECUTION_ERROR_702

**Message Template:**  
"Error executing plugin '{plugin_name}': {reason}"

**Common Causes:**
- Plugin code has an error
- Plugin received invalid inputs
- Plugin encountered a runtime error

**Recommended Fix:**
- Check plugin logs for detailed errors
- Verify plugin inputs
- Contact plugin maintainer if necessary

### PLUGIN_VALIDATION_ERROR_703

**Message Template:**  
"Plugin validation error for '{plugin_name}': {reason}"

**Common Causes:**
- Plugin doesn't meet framework requirements
- Plugin manifest is invalid
- Plugin security validation failed

**Recommended Fix:**
- Update plugin to meet requirements
- Fix plugin manifest
- Address security issues in the plugin

## Unknown Errors (900-999)

### UNKNOWN_ERROR_901

**Message Template:**  
"An unexpected error occurred: {message}"

**Common Causes:**
- Unhandled exceptions
- Bug in the framework or application
- System-level issues

**Recommended Fix:**
- Check the detailed error message
- Review logs for additional context
- Report the issue to framework maintainers 