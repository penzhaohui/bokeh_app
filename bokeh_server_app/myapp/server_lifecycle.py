# coding=utf-8
def on_server_loaded(server_context):
    ''' If present, this function is called when the server first starts. '''
    print('The on_server_loaded event is fired.')
    pass

def on_server_unloaded(server_context):
    ''' If present, this function is called when the server shuts down. '''
    print('The on_server_unloaded event is fired.')
    pass

def on_session_created(session_context):
    ''' If present, this function is called when a session is created. '''
    print('The on_session_created event is fired.')
    sessions = session_context.server_context.sessions
    session_count = len(sessions)
    print('{session_count} sessions are created.'.format(session_count=session_count))
    for session in session_context.server_context.sessions:
        print('session id: {session_id}, destroyed:{destroyed}'.format(session_id=session.id, destroyed=session.destroyed))
    pass

def on_session_destroyed(session_context):
    ''' If present, this function is called when a session is closed. '''
    sessions = session_context.server_context.sessions
    session_count = len(sessions)
    print('{session_count} sessions are created.'.format(session_count=session_count))
    for session in session_context.server_context.sessions:
        print('session id: {session_id}, destroyed:{destroyed}'.format(session_id=session.id, destroyed=session.destroyed))
    print('session id: {session_id}, destroyed:{destroyed}'.format(session_id=session_context.session.id, destroyed=session_context.session.destroyed))
    pass