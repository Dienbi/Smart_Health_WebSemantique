from django.shortcuts import render

def test_ai_view(request):
    """Render the AI test page"""
    return render(request, 'test_ai.html')
