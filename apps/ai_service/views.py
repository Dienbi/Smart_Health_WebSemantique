from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from apps.sparql_service.client import SparqlClient
from apps.sparql_service.formatter import SparqlResultFormatter
from .gemini_service import GeminiAIService


@method_decorator(csrf_exempt, name='dispatch')
class AIQueryView(APIView):
    """API endpoint for AI-powered queries"""
    permission_classes = [AllowAny]  # Allow unauthenticated access for testing
    authentication_classes = []  # Disable authentication for testing
    
    def post(self, request):
        """Process natural language prompt using real AI"""
        prompt = request.data.get('prompt', '')
        user_id = request.data.get('user_id', None)
        
        if not prompt:
            return Response(
                {'error': 'Prompt is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Initialize AI service
            ai_service = GeminiAIService()
            
            # Check if AI is configured
            if not ai_service.enabled:
                return Response({
                    'success': False,
                    'error': 'AI service not configured',
                    'setup_instructions': [
                        '1. Get free API key: https://makersuite.google.com/app/apikey',
                        '2. Add to .env file: GEMINI_API_KEY=your_key_here',
                        '3. Restart Django server'
                    ]
                }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
            # Extract user ID if not provided
            if not user_id:
                entities = ai_service.extract_entities(prompt)
                user_id = entities.get('user_id')
            
            # Analyze intent using AI
            intent = ai_service.analyze_intent(prompt)
            
            # Generate SPARQL query using AI
            sparql_query, error = ai_service.generate_sparql(prompt, user_id)
            
            if error:
                return Response({
                    'success': False,
                    'error': error,
                    'prompt': prompt
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Execute query based on intent
            client = SparqlClient()
            
            # Determine if it's a modification query
            is_modification = any(keyword in sparql_query.upper() for keyword in ['INSERT', 'DELETE', 'UPDATE'])
            
            if is_modification:
                # Execute update query
                success = client.execute_update(sparql_query)
                
                if success:
                    # Get operation type
                    operation = 'unknown'
                    if 'INSERT DATA' in sparql_query.upper():
                        operation = 'insert'
                    elif 'DELETE' in sparql_query.upper() and 'INSERT' in sparql_query.upper():
                        operation = 'update'
                    elif 'DELETE' in sparql_query.upper():
                        operation = 'delete'
                    
                    return Response({
                        'success': True,
                        'prompt': prompt,
                        'intent': intent,
                        'action': operation,
                        'user_id': user_id,
                        'sparql_query': sparql_query,
                        'message': f'Data {operation}ed successfully',
                        'ai_powered': True,
                        'ai_model': 'Google Gemini Pro'
                    })
                else:
                    return Response({
                        'success': False,
                        'error': 'Failed to execute modification query',
                        'sparql_query': sparql_query
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Execute select query
                results = client.execute_query(sparql_query)
                
                # Format results
                formatted_results = SparqlResultFormatter.format_results(results)
                
                return Response({
                    'success': True,
                    'prompt': prompt,
                    'intent': intent,
                    'action': 'query',
                    'user_id': user_id,
                    'sparql_query': sparql_query,
                    'results_count': len(formatted_results),
                    'results': formatted_results,
                    'ai_powered': True,
                    'ai_model': 'Google Gemini Pro'
                })
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error in AIQueryView: {error_details}")  # Log to console
            return Response(
                {
                    'success': False,
                    'error': str(e),
                    'error_type': type(e).__name__,
                    'message': 'An error occurred while processing your query',
                    'details': error_details if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get(self, request):
        """Get example prompts and usage information"""
        examples = {
            'query_examples': [
                {
                    'prompt': 'Show me all users',
                    'description': 'Retrieves all users from the system',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'What are the activities for user 1?',
                    'description': 'Gets activity logs for a specific user',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'Show me health metrics for user 1',
                    'description': 'Retrieves health metrics for a specific user',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'What meals does user 1 have?',
                    'description': 'Gets meal information for a specific user',
                    'type': 'SELECT'
                },
                {
                    'prompt': 'Show me all challenges',
                    'description': 'Lists all available challenges',
                    'type': 'SELECT'
                }
            ],
            'insert_examples': [
                {
                    'prompt': 'Add a new user named Alice with email alice@example.com',
                    'description': 'Creates a new user in the system',
                    'type': 'INSERT'
                },
                {
                    'prompt': 'Create a cardio activity called Running',
                    'description': 'Adds a new cardio activity',
                    'type': 'INSERT'
                },
                {
                    'prompt': 'Add a breakfast meal with 500 calories',
                    'description': 'Creates a new breakfast meal entry',
                    'type': 'INSERT'
                },
                {
                    'prompt': 'Create a new challenge called 30-Day Fitness',
                    'description': 'Adds a new challenge/defi',
                    'type': 'INSERT'
                }
            ],
            'update_examples': [
                {
                    'prompt': 'Update user Alice email to newalice@example.com',
                    'description': 'Changes the email of an existing user',
                    'type': 'UPDATE'
                },
                {
                    'prompt': 'Change the duration of Running activity to 45 minutes',
                    'description': 'Modifies an activity\'s duration',
                    'type': 'UPDATE'
                },
                {
                    'prompt': 'Set meal calories to 600 for breakfast',
                    'description': 'Updates the calorie count of a meal',
                    'type': 'UPDATE'
                }
            ],
            'delete_examples': [
                {
                    'prompt': 'Delete user Alice',
                    'description': 'Removes a user from the system',
                    'type': 'DELETE'
                },
                {
                    'prompt': 'Remove activity Running',
                    'description': 'Deletes an activity',
                    'type': 'DELETE'
                },
                {
                    'prompt': 'Delete the breakfast meal',
                    'description': 'Removes a meal entry',
                    'type': 'DELETE'
                }
            ],
            'usage': {
                'endpoint': '/api/ai/query/',
                'method': 'POST',
                'body': {
                    'prompt': 'Your natural language query/command',
                    'user_id': 'Optional: specific user ID (can be extracted from prompt)'
                }
            },
            'capabilities': [
                'Query data with natural language (SELECT)',
                'Insert new data (INSERT)',
                'Update existing data (UPDATE)',
                'Delete data (DELETE)',
                'AI-powered intent detection',
                'Automatic entity extraction'
            ]
        }
        
        return Response(examples)
