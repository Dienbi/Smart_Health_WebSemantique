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
import logging
import re

logger = logging.getLogger(__name__)


def sync_delete_from_fuseki_to_django(sparql_query):
    """
    Synchronize DELETE operations from Fuseki to Django
    Detects DELETE operations on HealthMetric and HealthRecord and deletes them from Django
    """
    try:
        # Check if it's a DELETE operation
        if 'DELETE' not in sparql_query.upper():
            return False
        
        # Parse HealthMetric DELETE operations
        # Pattern: DELETE WHERE { ?metric a sh:HealthMetric ; sh:healthMetricName "name" . ?metric ?p ?o }
        health_metric_pattern = r'DELETE\s+WHERE\s*\{[^}]*\?metric\s+a\s+sh:HealthMetric[^}]*sh:healthMetricName\s+"([^"]+)"[^}]*\?metric\s+\?p\s+\?o[^}]*\}'
        match = re.search(health_metric_pattern, sparql_query, re.IGNORECASE | re.DOTALL)
        
        if match:
            metric_name = match.group(1)
            logger.info(f"Detected DELETE operation for HealthMetric: {metric_name}")
            
            # Import here to avoid circular imports
            from apps.health_records.models import HealthMetric
            
            # Find and delete the metric in Django
            try:
                metric = HealthMetric.objects.get(metric_name=metric_name)
                metric_id = metric.health_metric_id
                metric.delete()
                logger.info(f"HealthMetric '{metric_name}' (ID: {metric_id}) deleted from Django")
                return True
            except HealthMetric.DoesNotExist:
                logger.warning(f"HealthMetric '{metric_name}' not found in Django, skipping sync")
                return False
            except Exception as e:
                logger.error(f"Error deleting HealthMetric '{metric_name}' from Django: {str(e)}")
                return False
        
        # Parse HealthRecord DELETE operations
        # Pattern: DELETE WHERE { ?record a sh:HealthRecord ; sh:healthRecordId ?id . ?record ?p ?o }
        # Or: DELETE WHERE { ?record a sh:HealthRecord ; sh:healthRecordDescription "desc" . ?record ?p ?o }
        health_record_pattern = r'DELETE\s+WHERE\s*\{[^}]*\?record\s+a\s+sh:HealthRecord[^}]*sh:healthRecordId\s+(\d+)[^}]*\?record\s+\?p\s+\?o[^}]*\}'
        match = re.search(health_record_pattern, sparql_query, re.IGNORECASE | re.DOTALL)
        
        if match:
            record_id = int(match.group(1))
            logger.info(f"Detected DELETE operation for HealthRecord: {record_id}")
            
            # Import here to avoid circular imports
            from apps.health_records.models import HealthRecord
            
            # Find and delete the record in Django
            try:
                record = HealthRecord.objects.get(health_record_id=record_id)
                record.delete()
                logger.info(f"HealthRecord (ID: {record_id}) deleted from Django")
                return True
            except HealthRecord.DoesNotExist:
                logger.warning(f"HealthRecord (ID: {record_id}) not found in Django, skipping sync")
                return False
            except Exception as e:
                logger.error(f"Error deleting HealthRecord (ID: {record_id}) from Django: {str(e)}")
                return False
        
        return False
    except Exception as e:
        logger.error(f"Error in sync_delete_from_fuseki_to_django: {str(e)}")
        return False


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
            try:
                sparql_query, error = ai_service.generate_sparql(prompt, user_id)
                
                if error:
                    return Response({
                        'success': False,
                        'error': error,
                        'prompt': prompt
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as ai_error:
                import traceback
                logger.error(f"Error generating SPARQL query: {str(ai_error)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                return Response({
                    'success': False,
                    'error': f'Error generating SPARQL query: {str(ai_error)}',
                    'prompt': prompt,
                    'traceback': traceback.format_exc() if settings.DEBUG else None
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Execute query based on intent
            client = SparqlClient()
            
            # Determine if it's a modification query
            is_modification = any(keyword in sparql_query.upper() for keyword in ['INSERT', 'DELETE', 'UPDATE'])
            
            if is_modification:
                # Execute update query
                try:
                    # Synchronize DELETE operations from Fuseki to Django BEFORE executing
                    if 'DELETE' in sparql_query.upper() and 'INSERT' not in sparql_query.upper():
                        sync_delete_from_fuseki_to_django(sparql_query)
                    
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
                except Exception as e:
                    import urllib.error
                    import traceback
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # Check for connection errors (more comprehensive)
                    is_connection_error = (
                        isinstance(e, urllib.error.URLError) or
                        isinstance(e, ConnectionError) or
                        'ConnectionRefusedError' in error_msg or
                        'WinError 10061' in error_msg or
                        'Connection refused' in error_msg.lower() or
                        'cannot connect' in error_msg.lower() or
                        'target machine actively refused' in error_msg.lower() or
                        error_type == 'ConnectionRefusedError'
                    )
                    
                    if is_connection_error:
                        return Response({
                            'success': False,
                            'error': 'Fuseki server is not running',
                            'message': 'Cannot connect to Fuseki server. Please start Fuseki server first.',
                            'setup_instructions': [
                                '1. Start Fuseki server:',
                                '   Option A - Using Docker:',
                                '   docker-compose up -d fuseki',
                                '   ',
                                '   Option B - Manual (if installed):',
                                '   cd C:\\apache-jena-fuseki-5.2.0',
                                '   .\\fuseki-server.bat --update --mem /smarthealth',
                                '2. Verify Fuseki is running at: http://localhost:3030',
                                '3. Retry your operation after starting Fuseki'
                            ],
                            'sparql_query': sparql_query,
                            'error_details': error_msg if settings.DEBUG else None
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    else:
                        # Log the error for debugging
                        logger.error(f"SPARQL update error: {error_msg}")
                        logger.error(f"SPARQL query: {sparql_query}")
                        logger.error(f"Error type: {error_type}")
                        if settings.DEBUG:
                            logger.error(f"Traceback: {traceback.format_exc()}")
                        
                        return Response({
                            'success': False,
                            'error': f'Error executing SPARQL update: {error_msg}',
                            'message': 'The SPARQL query failed. Please check the query syntax and try again.',
                            'sparql_query': sparql_query,
                            'error_type': error_type,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                # Execute select query
                try:
                    results = client.execute_query(sparql_query)
                    
                    # Format results
                    try:
                        formatted_results = SparqlResultFormatter.format_results(results)
                        results_count = len(formatted_results) if formatted_results else 0
                    except Exception as format_error:
                        import traceback
                        logger.error(f"Error formatting SPARQL results: {str(format_error)}")
                        logger.error(f"Raw results: {results}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return Response({
                            'success': False,
                            'error': f'Error formatting SPARQL results: {str(format_error)}',
                            'sparql_query': sparql_query,
                            'raw_results': results if settings.DEBUG else None,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                    
                    # Return successful response
                    try:
                        return Response({
                            'success': True,
                            'prompt': prompt,
                            'intent': intent,
                            'action': 'query',
                            'user_id': user_id,
                            'sparql_query': sparql_query,
                            'results_count': results_count,
                            'results': formatted_results,
                            'ai_powered': True,
                            'ai_model': 'Google Gemini Pro'
                        })
                    except Exception as response_error:
                        import traceback
                        logger.error(f"Error creating response: {str(response_error)}")
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        return Response({
                            'success': False,
                            'error': f'Error creating response: {str(response_error)}',
                            'sparql_query': sparql_query,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                except Exception as e:
                    import urllib.error
                    import traceback
                    error_msg = str(e)
                    error_type = type(e).__name__
                    
                    # Check for connection errors (more comprehensive)
                    is_connection_error = (
                        isinstance(e, urllib.error.URLError) or
                        isinstance(e, ConnectionError) or
                        'ConnectionRefusedError' in error_msg or
                        'WinError 10061' in error_msg or
                        'Connection refused' in error_msg.lower() or
                        'cannot connect' in error_msg.lower() or
                        'target machine actively refused' in error_msg.lower() or
                        error_type == 'ConnectionRefusedError'
                    )
                    
                    if is_connection_error:
                        return Response({
                            'success': False,
                            'error': 'Fuseki server is not running',
                            'message': 'Cannot connect to Fuseki server. Please start Fuseki server first.',
                            'setup_instructions': [
                                '1. Start Fuseki server:',
                                '   Option A - Using Docker:',
                                '   docker-compose up -d fuseki',
                                '   ',
                                '   Option B - Manual (if installed):',
                                '   cd C:\\apache-jena-fuseki-5.2.0',
                                '   .\\fuseki-server.bat --update --mem /smarthealth',
                                '2. Verify Fuseki is running at: http://localhost:3030',
                                '3. Refresh this page after starting Fuseki'
                            ],
                            'sparql_query': sparql_query,
                            'error_details': error_msg if settings.DEBUG else None
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    else:
                        return Response({
                            'success': False,
                            'error': f'Error executing SPARQL query: {error_msg}',
                            'sparql_query': sparql_query,
                            'error_type': error_type,
                            'traceback': traceback.format_exc() if settings.DEBUG else None
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Log to console and logger
            logger.error(f"Error in AIQueryView: {error_type}: {error_msg}")
            logger.error(f"Traceback: {error_details}")
            print(f"Error in AIQueryView: {error_type}: {error_msg}")
            print(f"Traceback: {error_details}")
            
            # Return error response
            try:
                return Response(
                    {
                        'success': False,
                        'error': error_msg,
                        'error_type': error_type,
                        'message': 'An error occurred while processing your query',
                        'traceback': error_details if settings.DEBUG else None
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as response_error:
                # If even error response fails, return minimal response
                logger.error(f"Failed to create error response: {str(response_error)}")
                return Response(
                    {
                        'success': False,
                        'error': 'Internal server error',
                        'error_type': error_type
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
