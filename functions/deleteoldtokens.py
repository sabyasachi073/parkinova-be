from datetime import datetime, timezone
from models.tokenblocklist import TokenBlocklist
from extensions import scheduler, db

def delete_old_tokens():
    try:
        with scheduler.app.app_context():
            now = datetime.now(timezone.utc)
            tokens_to_delete = TokenBlocklist.query.filter(TokenBlocklist.expires_at < now).all()
            for token in tokens_to_delete:  
                db.session.delete(token)
        
            db.session.commit()
    except Exception as e:
        print(str(e))
        


