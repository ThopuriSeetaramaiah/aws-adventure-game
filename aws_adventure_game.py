#!/usr/bin/env python3
"""
AWS Adventure Game - A text-based adventure game for the AWS Community Game Challenge
"""

import os
import sys
import time
import random
import json
from typing import Dict, List, Any, Tuple

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

class Player:
    def __init__(self, name: str):
        self.name = name
        self.inventory = []
        self.skills = {
            "compute": 1,
            "storage": 1,
            "networking": 1,
            "security": 1,
            "serverless": 1
        }
        self.health = 100
        self.score = 0
        self.current_location = "cloud_academy"
    
    def add_to_inventory(self, item: str) -> None:
        """Add an item to the player's inventory"""
        self.inventory.append(item)
        print(f"{Colors.GREEN}Added {item} to your inventory!{Colors.ENDC}")
    
    def improve_skill(self, skill: str, amount: int = 1) -> None:
        """Improve a player's skill"""
        if skill in self.skills:
            self.skills[skill] += amount
            print(f"{Colors.BLUE}Your {skill} skill increased to {self.skills[skill]}!{Colors.ENDC}")
        else:
            print(f"{Colors.RED}Invalid skill: {skill}{Colors.ENDC}")
    
    def take_damage(self, amount: int) -> None:
        """Player takes damage"""
        self.health -= amount
        print(f"{Colors.RED}You took {amount} damage! Health: {self.health}/100{Colors.ENDC}")
        if self.health <= 0:
            self.game_over("You ran out of health!")
    
    def heal(self, amount: int) -> None:
        """Player heals"""
        self.health = min(100, self.health + amount)
        print(f"{Colors.GREEN}You healed {amount} points! Health: {self.health}/100{Colors.ENDC}")
    
    def add_score(self, points: int) -> None:
        """Add points to player's score"""
        self.score += points
        print(f"{Colors.YELLOW}You gained {points} points! Score: {self.score}{Colors.ENDC}")
    
    def game_over(self, reason: str) -> None:
        """End the game"""
        print(f"\n{Colors.RED}{Colors.BOLD}GAME OVER: {reason}{Colors.ENDC}")
        print(f"\n{Colors.YELLOW}Final Score: {self.score}{Colors.ENDC}")
        print(f"\nThanks for playing, {self.name}!")
        sys.exit(0)
    
    def show_status(self) -> None:
        """Display player status"""
        print(f"\n{Colors.BOLD}=== {self.name}'s Status ==={Colors.ENDC}")
        print(f"Health: {self.health}/100")
        print(f"Score: {self.score}")
        print(f"Location: {self.current_location}")
        print("\nSkills:")
        for skill, level in self.skills.items():
            print(f"  {skill.capitalize()}: {level}")
        print("\nInventory:")
        if self.inventory:
            for item in self.inventory:
                print(f"  - {item}")
        else:
            print("  (empty)")
        print("")

class Game:
    def __init__(self):
        self.player = None
        self.locations = self.load_game_data()
        
    def load_game_data(self) -> Dict:
        """Load game data from a file or use default data"""
        # In a real game, we might load this from a JSON file
        return {
            "cloud_academy": {
                "name": "AWS Cloud Academy",
                "description": "The starting point of your AWS adventure. Here you can learn the basics of AWS services.",
                "options": [
                    {"text": "Take the EC2 course", "destination": "ec2_lab", "skill_gain": {"compute": 1}},
                    {"text": "Learn about S3", "destination": "s3_lab", "skill_gain": {"storage": 1}},
                    {"text": "Study networking", "destination": "vpc_lab", "skill_gain": {"networking": 1}},
                    {"text": "Check your status", "action": "status"}
                ]
            },
            "ec2_lab": {
                "name": "EC2 Laboratory",
                "description": "You're in a virtual lab environment learning about EC2 instances. The terminal shows various instance types.",
                "options": [
                    {"text": "Launch a t2.micro instance", "action": "ec2_launch", "skill_check": {"compute": 2}},
                    {"text": "Configure security groups", "action": "security_group", "skill_check": {"security": 2}},
                    {"text": "Return to Cloud Academy", "destination": "cloud_academy"},
                    {"text": "Check your status", "action": "status"}
                ]
            },
            "s3_lab": {
                "name": "S3 Storage Workshop",
                "description": "You're surrounded by virtual storage buckets. A console displays S3 commands and best practices.",
                "options": [
                    {"text": "Create a new bucket", "action": "create_bucket", "skill_check": {"storage": 2}},
                    {"text": "Configure bucket policies", "action": "bucket_policy", "skill_check": {"security": 2}},
                    {"text": "Return to Cloud Academy", "destination": "cloud_academy"},
                    {"text": "Check your status", "action": "status"}
                ]
            },
            "vpc_lab": {
                "name": "VPC Networking Center",
                "description": "A complex diagram of network connections is displayed on a large screen. Subnets, route tables, and gateways are highlighted.",
                "options": [
                    {"text": "Design a multi-AZ architecture", "action": "multi_az", "skill_check": {"networking": 2}},
                    {"text": "Configure a NAT Gateway", "action": "nat_gateway", "skill_check": {"networking": 3}},
                    {"text": "Return to Cloud Academy", "destination": "cloud_academy"},
                    {"text": "Check your status", "action": "status"}
                ]
            },
            "lambda_workshop": {
                "name": "Serverless Workshop",
                "description": "A futuristic room with floating code snippets and event-driven architectures visualized in 3D.",
                "options": [
                    {"text": "Create a Lambda function", "action": "create_lambda", "skill_check": {"serverless": 2}},
                    {"text": "Set up API Gateway", "action": "api_gateway", "skill_check": {"networking": 2, "serverless": 1}},
                    {"text": "Return to Cloud Academy", "destination": "cloud_academy"},
                    {"text": "Check your status", "action": "status"}
                ]
            },
            "final_challenge": {
                "name": "AWS Certification Exam",
                "description": "You've reached the final challenge! Put your AWS knowledge to the test in this certification exam.",
                "options": [
                    {"text": "Take the exam", "action": "final_exam"},
                    {"text": "Return to Cloud Academy to study more", "destination": "cloud_academy"},
                    {"text": "Check your status", "action": "status"}
                ]
            }
        }
    
    def start(self) -> None:
        """Start the game"""
        self.clear_screen()
        self.print_title()
        print(f"{Colors.CYAN}Welcome to the AWS Adventure Game!{Colors.ENDC}")
        print("In this game, you'll navigate the AWS Cloud, learn new skills,")
        print("and face challenges to become an AWS expert.\n")
        
        name = input("Enter your name: ")
        self.player = Player(name)
        
        print(f"\nWelcome, {name}! Your AWS adventure begins now...\n")
        time.sleep(1)
        
        # Start at the Cloud Academy
        self.navigate_to("cloud_academy")
    
    def clear_screen(self) -> None:
        """Clear the terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_title(self) -> None:
        """Print the game title"""
        title = """
    █████╗ ██╗    ██╗███████╗     █████╗ ██████╗ ██╗   ██╗███████╗███╗   ██╗████████╗██╗   ██╗██████╗ ███████╗
   ██╔══██╗██║    ██║██╔════╝    ██╔══██╗██╔══██╗██║   ██║██╔════╝████╗  ██║╚══██╔══╝██║   ██║██╔══██╗██╔════╝
   ███████║██║ █╗ ██║███████╗    ███████║██║  ██║██║   ██║█████╗  ██╔██╗ ██║   ██║   ██║   ██║██████╔╝█████╗  
   ██╔══██║██║███╗██║╚════██║    ██╔══██║██║  ██║╚██╗ ██╔╝██╔══╝  ██║╚██╗██║   ██║   ██║   ██║██╔══██╗██╔══╝  
   ██║  ██║╚███╔███╔╝███████║    ██║  ██║██████╔╝ ╚████╔╝ ███████╗██║ ╚████║   ██║   ╚██████╔╝██║  ██║███████╗
   ╚═╝  ╚═╝ ╚══╝╚══╝ ╚══════╝    ╚═╝  ╚═╝╚═════╝   ╚═══╝  ╚══════╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚══════╝
        """
        print(f"{Colors.YELLOW}{title}{Colors.ENDC}")
    
    def navigate_to(self, location_key: str) -> None:
        """Navigate to a new location"""
        if location_key in self.locations:
            location = self.locations[location_key]
            self.player.current_location = location_key
            
            self.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.CYAN}=== {location['name']} ==={Colors.ENDC}")
            print(f"{Colors.CYAN}{location['description']}{Colors.ENDC}\n")
            
            self.show_options(location)
        else:
            print(f"{Colors.RED}Error: Location '{location_key}' not found!{Colors.ENDC}")
    
    def show_options(self, location: Dict) -> None:
        """Show available options at the current location"""
        print(f"{Colors.BOLD}What would you like to do?{Colors.ENDC}")
        
        for i, option in enumerate(location["options"], 1):
            print(f"{i}. {option['text']}")
        
        choice = self.get_valid_input(len(location["options"]))
        self.process_choice(location["options"][choice - 1])
    
    def get_valid_input(self, max_value: int) -> int:
        """Get valid numerical input from the user"""
        while True:
            try:
                choice = int(input("\nEnter your choice (1-" + str(max_value) + "): "))
                if 1 <= choice <= max_value:
                    return choice
                else:
                    print(f"{Colors.RED}Please enter a number between 1 and {max_value}.{Colors.ENDC}")
            except ValueError:
                print(f"{Colors.RED}Please enter a valid number.{Colors.ENDC}")
    
    def process_choice(self, option: Dict) -> None:
        """Process the player's choice"""
        # Check if this option requires a skill check
        if "skill_check" in option:
            if not self.skill_check(option["skill_check"]):
                # Failed the skill check
                return
        
        # Apply skill gains if any
        if "skill_gain" in option:
            for skill, amount in option["skill_gain"].items():
                self.player.improve_skill(skill, amount)
        
        # Process the action or destination
        if "destination" in option:
            self.navigate_to(option["destination"])
        elif "action" in option:
            self.perform_action(option["action"])
        else:
            print(f"{Colors.RED}Error: Invalid option configuration!{Colors.ENDC}")
    
    def skill_check(self, required_skills: Dict) -> bool:
        """Check if the player has the required skills"""
        for skill, level in required_skills.items():
            if self.player.skills.get(skill, 0) < level:
                print(f"\n{Colors.RED}You need {skill.capitalize()} level {level} to do this, but your level is {self.player.skills.get(skill, 0)}.{Colors.ENDC}")
                print(f"{Colors.YELLOW}Hint: Try improving your {skill} skill first!{Colors.ENDC}")
                input("\nPress Enter to continue...")
                self.navigate_to(self.player.current_location)
                return False
        return True
    
    def perform_action(self, action: str) -> None:
        """Perform a specific game action"""
        if action == "status":
            self.player.show_status()
            input("\nPress Enter to continue...")
            self.navigate_to(self.player.current_location)
        
        elif action == "ec2_launch":
            print(f"\n{Colors.GREEN}You successfully launched an EC2 instance!{Colors.ENDC}")
            print("The instance is now running and accessible.")
            self.player.add_to_inventory("EC2 Instance Key")
            self.player.add_score(10)
            self.player.improve_skill("compute")
            
            # Random event
            if random.random() < 0.3:
                print(f"\n{Colors.RED}Oh no! You forgot to set a proper security group and your instance was compromised!{Colors.ENDC}")
                self.player.take_damage(20)
            
            input("\nPress Enter to continue...")
            self.navigate_to("lambda_workshop")  # Progress to next area
        
        elif action == "security_group":
            print(f"\n{Colors.GREEN}You configured secure and efficient security groups!{Colors.ENDC}")
            print("Your instances are now protected from unauthorized access.")
            self.player.add_score(15)
            self.player.improve_skill("security", 2)
            
            input("\nPress Enter to continue...")
            self.navigate_to("lambda_workshop")  # Progress to next area
        
        elif action == "create_bucket":
            print(f"\n{Colors.GREEN}You created an S3 bucket with proper configurations!{Colors.ENDC}")
            print("The bucket is ready to store your application data securely.")
            self.player.add_to_inventory("S3 Access Key")
            self.player.add_score(10)
            self.player.improve_skill("storage")
            
            input("\nPress Enter to continue...")
            self.navigate_to("lambda_workshop")  # Progress to next area
        
        elif action == "bucket_policy":
            print(f"\n{Colors.GREEN}You implemented a secure bucket policy!{Colors.ENDC}")
            print("Your data is now protected with proper access controls.")
            self.player.add_score(15)
            self.player.improve_skill("security")
            self.player.improve_skill("storage")
            
            input("\nPress Enter to continue...")
            self.navigate_to("lambda_workshop")  # Progress to next area
        
        elif action == "multi_az":
            print(f"\n{Colors.GREEN}You designed a resilient multi-AZ architecture!{Colors.ENDC}")
            print("Your application can now withstand AZ failures.")
            self.player.add_score(20)
            self.player.improve_skill("networking", 2)
            
            input("\nPress Enter to continue...")
            self.navigate_to("lambda_workshop")  # Progress to next area
        
        elif action == "nat_gateway":
            print(f"\n{Colors.GREEN}You successfully configured a NAT Gateway!{Colors.ENDC}")
            print("Your private instances can now access the internet securely.")
            self.player.add_score(25)
            self.player.improve_skill("networking", 2)
            self.player.improve_skill("security")
            
            input("\nPress Enter to continue...")
            self.navigate_to("lambda_workshop")  # Progress to next area
        
        elif action == "create_lambda":
            print(f"\n{Colors.GREEN}You created a Lambda function that processes data automatically!{Colors.ENDC}")
            print("Your serverless application is now running efficiently.")
            self.player.add_to_inventory("Lambda Function URL")
            self.player.add_score(20)
            self.player.improve_skill("serverless", 2)
            
            input("\nPress Enter to continue...")
            self.navigate_to("final_challenge")  # Progress to final challenge
        
        elif action == "api_gateway":
            print(f"\n{Colors.GREEN}You set up an API Gateway to expose your Lambda functions!{Colors.ENDC}")
            print("Your serverless API is now accessible to clients.")
            self.player.add_score(25)
            self.player.improve_skill("networking")
            self.player.improve_skill("serverless", 2)
            
            input("\nPress Enter to continue...")
            self.navigate_to("final_challenge")  # Progress to final challenge
        
        elif action == "final_exam":
            self.run_final_exam()
        
        else:
            print(f"{Colors.RED}Error: Unknown action '{action}'!{Colors.ENDC}")
            input("\nPress Enter to continue...")
            self.navigate_to(self.player.current_location)
    
    def run_final_exam(self) -> None:
        """Run the final certification exam"""
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== AWS Certification Exam ==={Colors.ENDC}")
        print(f"{Colors.CYAN}This is your final challenge! Answer these AWS questions correctly to complete your journey.{Colors.ENDC}\n")
        
        questions = [
            {
                "question": "Which AWS service is used for storing objects?",
                "options": ["EC2", "S3", "RDS", "Lambda"],
                "correct": 1  # 0-indexed, so 1 means "S3"
            },
            {
                "question": "Which AWS service is used for serverless computing?",
                "options": ["EC2", "EBS", "Lambda", "RDS"],
                "correct": 2
            },
            {
                "question": "Which AWS service is used for virtual networking?",
                "options": ["S3", "VPC", "DynamoDB", "SQS"],
                "correct": 1
            },
            {
                "question": "Which storage class in S3 is designed for long-term archival?",
                "options": ["S3 Standard", "S3 Intelligent-Tiering", "S3 One Zone-IA", "S3 Glacier"],
                "correct": 3
            },
            {
                "question": "Which AWS service would you use to run a containerized application?",
                "options": ["EC2", "Lambda", "ECS/EKS", "S3"],
                "correct": 2
            }
        ]
        
        correct_answers = 0
        
        for i, q in enumerate(questions, 1):
            print(f"\n{Colors.BOLD}Question {i}:{Colors.ENDC} {q['question']}")
            for j, option in enumerate(q['options']):
                print(f"{j+1}. {option}")
            
            answer = self.get_valid_input(len(q['options'])) - 1
            
            if answer == q['correct']:
                print(f"{Colors.GREEN}Correct!{Colors.ENDC}")
                correct_answers += 1
                self.player.add_score(10)
            else:
                print(f"{Colors.RED}Incorrect! The correct answer was: {q['options'][q['correct']]}{Colors.ENDC}")
            
            time.sleep(1)
        
        # Calculate result
        score_percent = (correct_answers / len(questions)) * 100
        
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.CYAN}=== Exam Results ==={Colors.ENDC}")
        print(f"You answered {correct_answers} out of {len(questions)} questions correctly ({score_percent}%).")
        
        if score_percent >= 70:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Congratulations! You passed the AWS Certification Exam!{Colors.ENDC}")
            self.player.add_score(50)
            self.player.add_to_inventory("AWS Certification")
            
            print(f"\n{Colors.YELLOW}{Colors.BOLD}You have completed the AWS Adventure Game!{Colors.ENDC}")
            print(f"Final Score: {self.player.score}")
            print(f"\nThanks for playing, {self.player.name}!")
            
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}Unfortunately, you didn't pass the exam. You need at least 70% to pass.{Colors.ENDC}")
            print(f"{Colors.YELLOW}Don't worry, you can study more and try again!{Colors.ENDC}")
            
            input("\nPress Enter to continue...")
            self.navigate_to("cloud_academy")

if __name__ == "__main__":
    game = Game()
    game.start()
