# API Key Setup Script for Quizlet AI Quiz Generator
Write-Host "🔑 Setting up API Keys for Quizlet AI Quiz Generator" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green

Write-Host ""
Write-Host "📋 Available LLM Providers (with free tiers):" -ForegroundColor Cyan
Write-Host "1. Google AI (Gemini) - FREE tier available" -ForegroundColor White
Write-Host "2. Groq - FREE tier available" -ForegroundColor White
Write-Host "3. Cohere - FREE tier available" -ForegroundColor White
Write-Host "4. OpenAI - Paid only" -ForegroundColor Gray
Write-Host "5. Anthropic - Paid only" -ForegroundColor Gray
Write-Host "6. Mistral AI - Paid only" -ForegroundColor Gray
Write-Host "7. Ollama - Local installation" -ForegroundColor White

Write-Host ""
Write-Host "🎯 Recommended: Start with Google AI and Groq (both free)" -ForegroundColor Yellow
Write-Host ""

# Check current .env file
if (Test-Path ".env") {
    Write-Host "📁 Current .env file found" -ForegroundColor Green
    $envContent = Get-Content ".env"
    
    # Check which keys are already set
    $googleKey = $envContent | Where-Object { $_ -match "GOOGLE_API_KEY=" } | ForEach-Object { $_.Split("=")[1] }
    $groqKey = $envContent | Where-Object { $_ -match "GROQ_API_KEY=" } | ForEach-Object { $_.Split("=")[1] }
    $cohereKey = $envContent | Where-Object { $_ -match "COHERE_API_KEY=" } | ForEach-Object { $_.Split("=")[1] }
    
    Write-Host "Current API Key Status:" -ForegroundColor Cyan
    Write-Host "  Google AI: $(if($googleKey -and $googleKey -ne '') { '✅ Set' } else { '❌ Not set' })" -ForegroundColor $(if($googleKey -and $googleKey -ne '') { 'Green' } else { 'Red' })
    Write-Host "  Groq: $(if($groqKey -and $groqKey -ne '') { '✅ Set' } else { '❌ Not set' })" -ForegroundColor $(if($groqKey -and $groqKey -ne '') { 'Green' } else { 'Red' })
    Write-Host "  Cohere: $(if($cohereKey -and $cohereKey -ne '') { '✅ Set' } else { '❌ Not set' })" -ForegroundColor $(if($cohereKey -and $cohereKey -ne '') { 'Green' } else { 'Red' })
} else {
    Write-Host "❌ No .env file found. Creating one..." -ForegroundColor Red
}

Write-Host ""
Write-Host "🚀 Getting Free API Keys:" -ForegroundColor Cyan
Write-Host ""

# Google AI Setup
Write-Host "1️⃣ Google AI (Gemini) Setup:" -ForegroundColor Yellow
Write-Host "   • Go to: https://makersuite.google.com/app/apikey" -ForegroundColor White
Write-Host "   • Sign in with your Google account" -ForegroundColor White
Write-Host "   • Click 'Create API Key'" -ForegroundColor White
Write-Host "   • Copy the API key" -ForegroundColor White
Write-Host "   • Free tier: 15 requests/minute, 1500 requests/day" -ForegroundColor Green
Write-Host ""

# Groq Setup
Write-Host "2️⃣ Groq Setup:" -ForegroundColor Yellow
Write-Host "   • Go to: https://console.groq.com/keys" -ForegroundColor White
Write-Host "   • Sign up for a free account" -ForegroundColor White
Write-Host "   • Click 'Create API Key'" -ForegroundColor White
Write-Host "   • Copy the API key" -ForegroundColor White
Write-Host "   • Free tier: 100 requests/minute, unlimited requests" -ForegroundColor Green
Write-Host ""

# Cohere Setup
Write-Host "3️⃣ Cohere Setup:" -ForegroundColor Yellow
Write-Host "   • Go to: https://dashboard.cohere.com/api-keys" -ForegroundColor White
Write-Host "   • Sign up for a free account" -ForegroundColor White
Write-Host "   • Click 'Create API Key'" -ForegroundColor White
Write-Host "   • Copy the API key" -ForegroundColor White
Write-Host "   • Free tier: 100 requests/minute, 1000 requests/day" -ForegroundColor Green
Write-Host ""

Write-Host "💡 After getting your API keys, update your .env file:" -ForegroundColor Cyan
Write-Host ""
Write-Host "Example .env configuration:" -ForegroundColor White
Write-Host @"
# LLM Provider API Keys
GOOGLE_API_KEY=your-google-api-key-here
GROQ_API_KEY=your-groq-api-key-here
COHERE_API_KEY=your-cohere-api-key-here

# Optional (paid providers)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
MISTRAL_API_KEY=
OLLAMA_BASE_URL=http://localhost:11434
"@ -ForegroundColor Gray

Write-Host ""
Write-Host "🔧 To test your API keys after setting them up:" -ForegroundColor Cyan
Write-Host "   python test-api-keys.py" -ForegroundColor White
Write-Host ""
Write-Host "🎯 Ready to get started? Follow the steps above to get your free API keys!" -ForegroundColor Green 