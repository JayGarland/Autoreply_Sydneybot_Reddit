#!/usr/bin/env python3
"""
Simple one-shot test script for the Reddit bot.
Edit the settings below and run to test the bot.
"""

from log import logger
from AIbot_utils import task, ignored_content, pickle_path
import pickle

# TEST SETTINGS - Edit these to configure your test
TEST_METHOD = "at_me"    # Options: "at_me", "random", or None (auto)
DRY_RUN = False          # Set to False to actually post replies
VERBOSE = True          # Set to False for less logging

def save_ignored_content():
    """Save the ignored content to pickle file"""
    try:
        with open(pickle_path, "wb") as pkl:
            pickle.dump(ignored_content, pkl)
        logger.info(f"Saved {len(ignored_content)} ignored items to {pickle_path}")
    except Exception as e:
        logger.error(f"Failed to save ignored content: {e}")

def test_bot():
    """Run the bot once for testing"""
    
    # Configure logging
    if VERBOSE:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    logger.info("=" * 50)
    logger.info("STARTING ONE-SHOT BOT TEST")
    logger.info(f"Method: {TEST_METHOD or 'auto (based on cycle)'}")
    logger.info(f"Dry run: {DRY_RUN}")
    logger.info("=" * 50)
    
    # Override method if specified
    original_values = {}
    if TEST_METHOD:
        import AIbot_utils
        # Store original values
        original_values['random_check_rate'] = AIbot_utils.random_check_rate
        original_values['i'] = AIbot_utils.i
        
        logger.info(f"🔧 Overriding method to: {TEST_METHOD}")
        logger.info(f"📊 Original i={AIbot_utils.i}, random_check_rate={AIbot_utils.random_check_rate}")
        
        if TEST_METHOD == "random":
            # Force random mode: i % random_check_rate == 0, so set i=0 and random_check_rate=1
            AIbot_utils.i = 0
            AIbot_utils.random_check_rate = 1
        elif TEST_METHOD == "at_me":
            # Force at_me mode: i % random_check_rate != 0, so set i=1 and random_check_rate=2
            AIbot_utils.i = 1
            AIbot_utils.random_check_rate = 2
            
        logger.info(f"📊 Modified i={AIbot_utils.i}, random_check_rate={AIbot_utils.random_check_rate}")
        logger.info(f"🎯 Expected method: {TEST_METHOD}")
        logger.info(f"🔍 Check: i % random_check_rate = {AIbot_utils.i % AIbot_utils.random_check_rate}")
        if AIbot_utils.i % AIbot_utils.random_check_rate == 0:
            logger.info("🔄 Logic will use: random")
        else:
            logger.info("🎯 Logic will use: at_me")
    
    # Override reply function for dry run
    original_reply = None
    if DRY_RUN:
        import AIbot_utils
        
        def mock_reply(content, context, sub_user_nickname, bot_statement, bot_nickname, retry_count=0):
            logger.info("=" * 40)
            logger.info("🤖 SIMULATED REPLY DETECTED!")
            if hasattr(content, 'title'):
                logger.info(f"📝 Target: Submission by u/{content.author}")
                logger.info(f"📌 Title: {content.title}")
                if content.selftext:
                    logger.info(f"📄 Content: {content.selftext[:100]}...")
            else:
                logger.info(f"💬 Target: Comment by u/{content.author}")
                logger.info(f"💭 Comment: {content.body[:100]}...")
            
            logger.info(f"📊 Context length: {len(context)} characters")
            logger.info(f"👤 User nickname: {sub_user_nickname}")
            logger.info(f"🦆 Bot nickname: {bot_nickname}")
            
            # Show user history if present
            if "[system](#user_history)" in context:
                logger.info("✅ User history analysis included")
            else:
                logger.info("❌ No user history found")
                
            # Show user portrait if present  
            if "[system](#user_portrait)" in context:
                logger.info("✅ User portrait generation included")
            else:
                logger.info("❌ No user portrait found")
                
            logger.info("🚀 In real mode, bot would post reply now!")
            logger.info("=" * 40)
        
        original_reply = AIbot_utils.generate_reply
        AIbot_utils.generate_reply = mock_reply
    
    try:
        # Run the bot task once
        task()
        
        # Save any new ignored content
        save_ignored_content()
        
        logger.info("=" * 50)
        logger.info("✅ ONE-SHOT BOT TEST COMPLETED SUCCESSFULLY")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"❌ Bot test failed: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        # Restore original values if modified
        if TEST_METHOD and original_values:
            import AIbot_utils
            AIbot_utils.random_check_rate = original_values['random_check_rate']
            AIbot_utils.i = original_values['i']
            logger.info(f"🔧 Restored original values: i={AIbot_utils.i}, random_check_rate={AIbot_utils.random_check_rate}")
            
        if DRY_RUN and original_reply is not None:
            AIbot_utils.generate_reply = original_reply

if __name__ == "__main__":
    print("🦆 Reddit Bot One-Shot Test")
    print("=" * 30)
    print(f"Method: {TEST_METHOD or 'auto'}")
    print(f"Dry Run: {DRY_RUN}")
    print(f"Verbose: {VERBOSE}")
    print("=" * 30)
    print()
    
    test_bot()
