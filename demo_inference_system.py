#!/usr/bin/env python3
"""
Demo: Enhanced Agent Cards with Claude CLI Inference Results
Demonstrates the real-time inference monitoring system
"""

import requests
import time
import json
from datetime import datetime
import sys

def test_inference_api():
    """Test the inference API endpoints"""
    base_url = "http://localhost:8004"

    print("=" * 60)
    print("ENHANCED AGENT CARDS DEMO")
    print("Real-time Claude CLI Inference Monitoring")
    print("=" * 60)

    try:
        # Test health endpoint
        print("\n1. Testing Inference API Health...")
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            print("✅ Inference API is healthy")
            print(f"   Status: {response.json()['status']}")
        else:
            print("❌ Inference API health check failed")
            return False

        # Test system health
        print("\n2. Testing System Health...")
        response = requests.get(f"{base_url}/api/system/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ System Health: {data['status']}")
            print(f"   Health Score: {data['health_score']}%")
            print(f"   Online Agents: {data['online_agents']}/{data['total_agents']}")

        # Test real-time metrics
        print("\n3. Testing Real-time Metrics...")
        response = requests.get(f"{base_url}/api/realtime/metrics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Real-time metrics available")
            for agent_type, metrics in data['agents'].items():
                status_emoji = "🟢" if metrics['status'] == 'online' else "🔴" if metrics['status'] == 'offline' else "🟡"
                print(f"   {status_emoji} {agent_type.capitalize()}: {metrics['status']} | "
                      f"Confidence: {metrics['confidence']}% | "
                      f"Calls: {metrics['total_calls']}")

        # Test individual agent inferences
        print("\n4. Testing Agent Inferences...")
        agents = ['risk', 'strategy', 'funding', 'sentiment']

        for agent in agents:
            response = requests.get(f"{base_url}/api/agents/{agent}/inferences?limit=3", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ {agent.capitalize()} Agent: {data['count']} inferences")

                # Show latest inference if available
                if data['inferences']:
                    latest = data['inferences'][0]
                    confidence = latest.get('confidence', 0) * 100
                    processing_time = latest.get('processing_time', 0)
                    task = latest.get('input_data', {}).get('task', 'Unknown')

                    print(f"   Latest: {task[:50]}...")
                    print(f"   Confidence: {confidence:.1f}% | Time: {processing_time}ms")
            else:
                print(f"⚠️  {agent.capitalize()} Agent: API error")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Inference API")
        print("   Make sure the API is running on http://localhost:8004")
        print("   Run: python start_inference_monitoring.py")
        return False
    except Exception as e:
        print(f"❌ Error testing Inference API: {e}")
        return False

def demo_features():
    """Demonstrate the enhanced features"""
    print("\n" + "=" * 60)
    print("ENHANCED AGENT CARDS FEATURES")
    print("=" * 60)

    features = [
        {
            "title": "🔄 Real-time Inference Display",
            "description": "Shows latest Claude CLI inference results with confidence scores",
            "details": "• Task descriptions and completion status\n• Processing time in milliseconds\n• Success/error indicators"
        },
        {
            "title": "📊 Performance Metrics",
            "description": "Live monitoring of agent performance and health",
            "details": "• Confidence levels with color coding\n• Response time tracking\n• Uptime percentages"
        },
        {
            "title": "🎛️ Enhanced Controls",
            "description": "Elegant toggle switches with visual feedback",
            "details": "• Smooth animations and transitions\n• Status indicators (online/offline/pending)\n• Bulk agent control"
        },
        {
            "title": "🔔 Smart Notifications",
            "description": "Real-time alerts for agent status changes",
            "details": "• Success/error/info notifications\n• Auto-dismiss functionality\n• Mobile-responsive design"
        },
        {
            "title": "⚡ Auto-refresh System",
            "description": "Automatic inference updates every 30 seconds",
            "details": "• Only updates for active agents\n• Graceful error handling with fallback\n• Manual refresh buttons"
        }
    ]

    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['title']}")
        print(f"   {feature['description']}")
        print(f"   {feature['details']}")

    print("\n" + "=" * 60)
    print("FRONTEND INTEGRATION")
    print("=" * 60)

    frontend_info = [
        "✅ Enhanced CSS styling with animations",
        "✅ Real-time JavaScript integration",
        "✅ Fallback mock data for demo",
        "✅ Responsive design for all devices",
        "✅ Error handling and loading states",
        "✅ Color-coded confidence indicators",
        "✅ Time-based inference sorting"
    ]

    for info in frontend_info:
        print(f"   {info}")

def show_usage():
    """Show how to use the system"""
    print("\n" + "=" * 60)
    print("SYSTEM USAGE")
    print("=" * 60)

    print("\n📋 Steps to use the enhanced agent system:")
    print("1. Start the inference monitoring API:")
    print("   python start_inference_monitoring.py")

    print("\n2. Start the main dashboard:")
    print("   npx ts-node run.ts start")

    print("\n3. Open your browser to:")
    print("   http://localhost:9001/")

    print("\n4. Features available:")
    print("   • Toggle individual agents ON/OFF")
    print("   • View real-time inference results")
    print("   • Monitor agent performance metrics")
    print("   • Use bulk controls for all agents")
    print("   • Receive notifications for status changes")

    print("\n🔗 API Endpoints:")
    print("• Health: http://localhost:8004/api/health")
    print("• System: http://localhost:8004/api/system/summary")
    print("• Metrics: http://localhost:8004/api/realtime/metrics")
    print("• Agent inferences: http://localhost:8004/api/agents/{type}/inferences")

def main():
    """Main demo function"""
    print("[ENHANCED] Agent Cards with Claude CLI Inference Results")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test the API
    if test_inference_api():
        print("\n🎉 Inference API is working correctly!")

        # Show features
        demo_features()

        # Show usage
        show_usage()

        print("\n" + "=" * 60)
        print("✅ DEMO COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("\n💡 The enhanced agent cards now display:")
        print("   • Real-time Claude CLI inference results")
        print("   • Confidence scores and processing times")
        print("   • Elegant toggle switches with animations")
        print("   • Master control panel for bulk operations")
        print("   • Comprehensive error handling and fallbacks")

    else:
        print("\n❌ Demo failed - please check the API is running")
        print("   Run: python start_inference_monitoring.py")

if __name__ == "__main__":
    main()