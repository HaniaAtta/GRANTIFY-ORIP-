#!/bin/bash
# Quick script to check and fix virtual environment

echo "Checking virtual environment..."
echo ""

# Check if HandM/bin exists
if [ ! -d "HandM/bin" ]; then
    echo "❌ Error: HandM/bin directory not found!"
    echo "   Make sure you're in the project root directory"
    exit 1
fi

echo "✅ HandM/bin directory found"
echo ""

# Check if activate script exists
if [ ! -f "HandM/bin/activate" ]; then
    echo "❌ Error: HandM/bin/activate not found!"
    exit 1
fi

echo "✅ Activation script found"
echo ""

# Source the activation
source HandM/bin/activate

echo "Virtual environment activated!"
echo ""

# Check PATH
if echo $PATH | grep -q "HandM/bin"; then
    echo "✅ PATH includes HandM/bin"
else
    echo "⚠️  PATH doesn't include HandM/bin"
    echo "   Try: export PATH=\"HandM/bin:\$PATH\""
fi

echo ""

# Check Python
echo "Checking Python..."
if command -v python &> /dev/null; then
    echo "✅ python command found: $(which python)"
    python --version
elif command -v python3 &> /dev/null; then
    echo "✅ python3 command found: $(which python3)"
    python3 --version
    echo ""
    echo "💡 Tip: Use 'python3' instead of 'python', or create an alias:"
    echo "   alias python=python3"
else
    echo "❌ Neither python nor python3 found in PATH"
    echo ""
    echo "Available in HandM/bin:"
    ls -1 HandM/bin/ | grep python
fi

echo ""
echo "Current PATH:"
echo $PATH | tr ':' '\n' | grep -E "(HandM|python)" | head -5

