import discord
from discord.ext import commands, tasks
import json
import datetime
import asyncio
import random
from discord.ui import Button, View
import os

# Check if tasks.json exists, if not create it
if not os.path.exists('tasks.json'):
    with open('tasks.json', 'w') as f:
        json.dump({}, f)

# Load tasks from file
def load_tasks():
    try:
        with open('tasks.json', 'r') as f:
            return json.load(f)
    except:
        return {}

# Save tasks to file
def save_tasks(tasks_data):
    with open('tasks.json', 'w') as f:
        json.dump(tasks_data, f, indent=4)

class TaskManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks_data = load_tasks()
        # Format: {channel_id: {
        #   "tasks": [{"name": "Task name", "completed": False, "id": 1}],
        #   "days": 5,
        #   "setup_mode": False,
        #   "daily_tasks": {"day1": [task_ids], "day2": [task_ids]},
        #   "current_day": 1,
        #   "start_date": "2025-03-19"
        # }}
        self.setup_users = {}  # Users currently in setup mode
        self.daily_reminder.start()
        self.evening_check.start()

    async def distribute_tasks(self, channel_id):
        """Distribute tasks evenly across the specified days"""
        channel_data = self.tasks_data.get(str(channel_id), {})
        tasks = channel_data.get("tasks", [])
        days = channel_data.get("days", 1)
        
        # Only distribute tasks that are not completed
        incomplete_tasks = [task for task in tasks if not task["completed"]]
        
        # Reset daily tasks distribution
        daily_tasks = {}
        
        # Handle case where there are more days than tasks
        if len(incomplete_tasks) < days:
            # Distribute one task per day until we run out of tasks
            for day in range(1, len(incomplete_tasks) + 1):
                daily_tasks[f"day{day}"] = [incomplete_tasks[day-1]["id"]]
            
            # Add break days for the remaining days
            for day in range(len(incomplete_tasks) + 1, days + 1):
                daily_tasks[f"day{day}"] = []  # Empty list means break day
        else:
            # Distribute tasks evenly across days
            tasks_per_day = max(1, len(incomplete_tasks) // days)
            remainder = len(incomplete_tasks) % days
            
            start_idx = 0
            for day in range(1, days + 1):
                end_idx = start_idx + tasks_per_day
                if remainder > 0:
                    end_idx += 1
                    remainder -= 1
                    
                daily_tasks[f"day{day}"] = [task["id"] for task in incomplete_tasks[start_idx:end_idx]]
                start_idx = end_idx
        
        # Update the tasks data
        channel_data["daily_tasks"] = daily_tasks
        channel_data["current_day"] = 1
        channel_data["start_date"] = datetime.datetime.now().strftime("%Y-%m-%d")
        self.tasks_data[str(channel_id)] = channel_data
        save_tasks(self.tasks_data)

    @commands.command(name="setup")
    async def setup(self, ctx):
        """Set up task management for the current channel"""
        channel_id = str(ctx.channel.id)
        
        # Initialize tasks for the channel
        if channel_id not in self.tasks_data:
            self.tasks_data[channel_id] = {
                "tasks": [],
                "days": 0,
                "setup_mode": True,
                "daily_tasks": {},
                "current_day": 0,
                "start_date": None
            }
        else:
            self.tasks_data[channel_id]["setup_mode"] = True
        
        save_tasks(self.tasks_data)
        
        # Start the setup process
        self.setup_users[ctx.author.id] = {"channel_id": channel_id, "stage": "tasks"}
        
        # Send initial message
        embed = discord.Embed(
            title="📋 Task Management Setup",
            description="Give the name of the task or say `!save` to continue.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Handle messages for task setup"""
        if message.author.bot:
            return
        
        user_id = message.author.id
        
        if user_id in self.setup_users:
            setup_data = self.setup_users[user_id]
            channel_id = setup_data["channel_id"]
            
            # Check if the message is !save command
            if message.content.strip().lower() == "!save":
                # If in tasks stage, move to days stage
                if setup_data["stage"] == "tasks":
                    setup_data["stage"] = "days"
                    self.setup_users[user_id] = setup_data
                    
                    embed = discord.Embed(
                        title="📅 Task Duration",
                        description="How many days do you want to complete these tasks?",
                        color=discord.Color.blue()
                    )
                    await message.channel.send(embed=embed)
                return
            
            # Ignore other command messages
            if message.content.startswith('!'):
                return
            
            # Check if the user is in task input stage
            if setup_data["stage"] == "tasks":
                content = message.content.strip()
                
                # Add the task
                task_id = len(self.tasks_data[str(channel_id)]["tasks"]) + 1
                self.tasks_data[str(channel_id)]["tasks"].append({
                    "name": content,
                    "completed": False,
                    "id": task_id
                })
                save_tasks(self.tasks_data)
                
                embed = discord.Embed(
                    title="✅ Task Added",
                    description=f"Task `{content}` added. Add another task or say `!save` to continue.",
                    color=discord.Color.green()
                )
                await message.channel.send(embed=embed)
            
            # Check if the user is in days input stage
            elif setup_data["stage"] == "days":
                content = message.content.strip()
                
                try:
                    days = int(content)
                    if days <= 0:
                        raise ValueError("Days must be greater than 0")
                    
                    # Update the days
                    self.tasks_data[str(channel_id)]["days"] = days
                    self.tasks_data[str(channel_id)]["setup_mode"] = False
                    save_tasks(self.tasks_data)
                    
                    # Distribute tasks
                    await self.distribute_tasks(channel_id)
                    
                    # Remove the user from setup mode
                    del self.setup_users[user_id]
                    
                    embed = discord.Embed(
                        title="🎉 Setup Complete",
                        description=f"Task management setup complete! You have {days} days to complete all tasks.",
                        color=discord.Color.green()
                    )
                    await message.channel.send(embed=embed)
                    
                    # Show the task list
                    await self.show_task_list(message.channel, channel_id)
                except ValueError:
                    embed = discord.Embed(
                        title="❌ Invalid Input",
                        description="Please enter a valid number of days greater than 0.",
                        color=discord.Color.red()
                    )
                    await message.channel.send(embed=embed)

    async def show_task_list(self, channel, channel_id):
        """Show the task list for a channel"""
        channel_data = self.tasks_data.get(str(channel_id), {})
        tasks = channel_data.get("tasks", [])
        days = channel_data.get("days", 0)
        current_day = channel_data.get("current_day", 0)
        
        if not tasks:
            embed = discord.Embed(
                title="📋 Task List",
                description="No tasks available. Use `!add` to add tasks.",
                color=discord.Color.blue()
            )
            await channel.send(embed=embed)
            return
        
        # Create the task list embed
        embed = discord.Embed(
            title="📋 Task List",
            description=f"Day {current_day}/{days}",
            color=discord.Color.blue()
        )
        
        # Add tasks
        tasks_text = ""
        for task in tasks:
            status = "✅" if task["completed"] else "❌"
            tasks_text += f"{task['id']}. {status} {task['name']}\n"
        
        embed.add_field(name="Tasks", value=tasks_text or "No tasks", inline=False)
        
        # Add daily tasks if available
        daily_tasks = channel_data.get("daily_tasks", {})
        if daily_tasks and current_day > 0:
            today_tasks = daily_tasks.get(f"day{current_day}", [])
            if today_tasks:
                today_tasks_text = ""
                for task_id in today_tasks:
                    task = next((t for t in tasks if t["id"] == task_id), None)
                    if task:
                        status = "✅" if task["completed"] else "❌"
                        today_tasks_text += f"{task_id}. {status} {task['name']}\n"
                
                embed.add_field(name="Today's Tasks", value=today_tasks_text, inline=False)
            else:
                embed.add_field(name="Today's Tasks", value="Break day! No tasks for today.", inline=False)
        
        await channel.send(embed=embed)

    @commands.command(name="list")
    async def list_tasks(self, ctx):
        """List all tasks for the channel"""
        channel_id = str(ctx.channel.id)
        await self.show_task_list(ctx.channel, channel_id)

    @commands.command(name="add")
    async def add_task(self, ctx, *, task_name):
        """Add a task to the current list"""
        channel_id = str(ctx.channel.id)
        
        if channel_id not in self.tasks_data:
            self.tasks_data[channel_id] = {
                "tasks": [],
                "days": 0,
                "setup_mode": False,
                "daily_tasks": {},
                "current_day": 0,
                "start_date": None
            }
        
        # Add the task
        task_id = len(self.tasks_data[channel_id]["tasks"]) + 1
        self.tasks_data[channel_id]["tasks"].append({
            "name": task_name,
            "completed": False,
            "id": task_id
        })
        save_tasks(self.tasks_data)
        
        # If days are set, redistribute tasks
        if self.tasks_data[channel_id]["days"] > 0:
            await self.distribute_tasks(channel_id)
        
        embed = discord.Embed(
            title="✅ Task Added",
            description=f"Task `{task_name}` added.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @commands.command(name="remove")
    async def remove_task(self, ctx, task_id: int):
        """Remove a task from the list"""
        channel_id = str(ctx.channel.id)
        
        if channel_id not in self.tasks_data:
            embed = discord.Embed(
                title="❌ Error",
                description="No tasks found for this channel.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        tasks = self.tasks_data[channel_id]["tasks"]
        task = next((t for t in tasks if t["id"] == task_id), None)
        
        if task:
            self.tasks_data[channel_id]["tasks"].remove(task)
            save_tasks(self.tasks_data)
            
            # If days are set, redistribute tasks
            if self.tasks_data[channel_id]["days"] > 0:
                await self.distribute_tasks(channel_id)
            
            embed = discord.Embed(
                title="🗑️ Task Removed",
                description=f"Task `{task['name']}` has been removed.",
                color=discord.Color.green()
            )
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Task with ID {task_id} not found.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)

    @commands.command(name="clear")
    async def clear_tasks(self, ctx):
        """Clear all tasks and reset the task management for the channel"""
        channel_id = str(ctx.channel.id)
        
        if channel_id not in self.tasks_data:
            embed = discord.Embed(
                title="❌ Error",
                description="No tasks found for this channel.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Reset all data for this channel
        self.tasks_data[channel_id] = {
            "tasks": [],
            "days": 0,
            "setup_mode": False,
            "daily_tasks": {},
            "current_day": 0,
            "start_date": None
        }
        save_tasks(self.tasks_data)
        
        # Remove any users in setup mode for this channel
        users_to_remove = []
        for user_id, setup_data in self.setup_users.items():
            if setup_data["channel_id"] == channel_id:
                users_to_remove.append(user_id)
        
        for user_id in users_to_remove:
            if user_id in self.setup_users:
                del self.setup_users[user_id]
        
        embed = discord.Embed(
            title="🧹 Tasks Cleared",
            description="All tasks and settings have been cleared for this channel.",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

    @tasks.loop(minutes=1)
    async def daily_reminder(self):
        """Send daily task reminders at 6 UTC"""
        now = datetime.datetime.utcnow()
        if now.hour == 6 and now.minute == 0:
            for channel_id, channel_data in self.tasks_data.items():
                if channel_data.get("current_day", 0) > 0:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        daily_tasks = channel_data.get("daily_tasks", {})
                        current_day = channel_data.get("current_day", 0)
                        today_tasks = daily_tasks.get(f"day{current_day}", [])
                        
                        embed = discord.Embed(
                            title="📅 Today's Tasks",
                            description=f"Day {current_day}/{channel_data.get('days', 0)}",
                            color=discord.Color.blue()
                        )
                        
                        if today_tasks:
                            tasks_text = ""
                            for task_id in today_tasks:
                                task = next((t for t in channel_data["tasks"] if t["id"] == task_id), None)
                                if task:
                                    status = "✅" if task["completed"] else "❌"
                                    tasks_text += f"{task_id}. {status} {task['name']}\n"
                            
                            embed.add_field(name="Tasks", value=tasks_text, inline=False)
                        else:
                            embed.add_field(name="Tasks", value="Break day! No tasks for today.", inline=False)
                            
                        await channel.send(embed=embed)

    @tasks.loop(minutes=1)
    async def evening_check(self):
        """Check task completion at 22 UTC"""
        now = datetime.datetime.utcnow()
        if now.hour == 22 and now.minute == 0:
            for channel_id, channel_data in self.tasks_data.items():
                if channel_data.get("current_day", 0) > 0:
                    channel = self.bot.get_channel(int(channel_id))
                    if channel:
                        daily_tasks = channel_data.get("daily_tasks", {})
                        current_day = channel_data.get("current_day", 0)
                        today_tasks = daily_tasks.get(f"day{current_day}", [])
                        
                        if today_tasks:
                            # Create a view with buttons
                            view = TaskCompletionView(self, channel_id, today_tasks)
                            
                            embed = discord.Embed(
                                title="✅ Task Completion Check",
                                description="Did you complete today's tasks?",
                                color=discord.Color.gold()
                            )
                            
                            tasks_text = ""
                            for task_id in today_tasks:
                                task = next((t for t in channel_data["tasks"] if t["id"] == task_id), None)
                                if task:
                                    status = "✅" if task["completed"] else "❌"
                                    tasks_text += f"{task_id}. {status} {task['name']}\n"
                            
                            embed.add_field(name="Today's Tasks", value=tasks_text, inline=False)
                            await channel.send(embed=embed, view=view)
                        else:
                            # It's a break day, just advance to the next day
                            await self.advance_day(channel_id)
                            
                            embed = discord.Embed(
                                title="😌 Break Day Complete",
                                description="Today was a break day. Moving to the next day.",
                                color=discord.Color.green()
                            )
                            await channel.send(embed=embed)

    @daily_reminder.before_loop
    @evening_check.before_loop
    async def before_tasks(self):
        """Wait until the bot is ready before starting tasks"""
        await self.bot.wait_until_ready()

    async def check_completion(self, channel_id):
        """Check if all tasks are completed"""
        channel_data = self.tasks_data.get(str(channel_id), {})
        tasks = channel_data.get("tasks", [])
        days = channel_data.get("days", 0)
        current_day = channel_data.get("current_day", 0)
        
        # Check if all tasks are completed
        all_completed = all(task["completed"] for task in tasks)
        
        # Check if we've reached the end of the days
        end_of_days = current_day >= days
        
        if all_completed or end_of_days:
            # Send the archived list
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                embed = discord.Embed(
                    title="📊 Task Completion Report",
                    description=f"Period: {channel_data.get('start_date', 'Unknown')} to {datetime.datetime.now().strftime('%Y-%m-%d')}",
                    color=discord.Color.purple()
                )
                
                completed_tasks = [task for task in tasks if task["completed"]]
                incompleted_tasks = [task for task in tasks if not task["completed"]]
                
                if completed_tasks:
                    completed_text = "\n".join([f"{task['id']}. {task['name']}" for task in completed_tasks])
                    embed.add_field(name="✅ Completed Tasks", value=completed_text, inline=False)
                else:
                    embed.add_field(name="✅ Completed Tasks", value="None", inline=False)
                
                if incompleted_tasks:
                    incompleted_text = "\n".join([f"{task['id']}. {task['name']}" for task in incompleted_tasks])
                    embed.add_field(name="❌ Incompleted Tasks", value=incompleted_text, inline=False)
                else:
                    embed.add_field(name="❌ Incompleted Tasks", value="None", inline=False)
                
                completion_rate = len(completed_tasks) / len(tasks) * 100 if tasks else 0
                embed.add_field(name="📈 Completion Rate", value=f"{completion_rate:.1f}%", inline=False)
                
                await channel.send(embed=embed)
                
                # Reset the tasks
                self.tasks_data[str(channel_id)] = {
                    "tasks": [],
                    "days": 0,
                    "setup_mode": False,
                    "daily_tasks": {},
                    "current_day": 0,
                    "start_date": None
                }
                save_tasks(self.tasks_data)
            
            return True
        
        return False

    async def advance_day(self, channel_id):
        """Advance to the next day"""
        channel_data = self.tasks_data.get(str(channel_id), {})
        current_day = channel_data.get("current_day", 0)
        days = channel_data.get("days", 0)
        
        if current_day < days:
            channel_data["current_day"] = current_day + 1
            self.tasks_data[str(channel_id)] = channel_data
            save_tasks(self.tasks_data)
            
            # Check if all tasks are now completed
            await self.check_completion(channel_id)
            
            return True
        
        return False

class TaskCompletionView(View):
    def __init__(self, cog, channel_id, today_tasks):
        super().__init__(timeout=86400)  # 24 hours timeout
        self.cog = cog
        self.channel_id = channel_id
        self.today_tasks = today_tasks

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Mark all tasks as completed
        channel_data = self.cog.tasks_data.get(str(self.channel_id), {})
        tasks = channel_data.get("tasks", [])
        
        for task_id in self.today_tasks:
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task:
                task["completed"] = True
        
        save_tasks(self.cog.tasks_data)
        
        # Advance to the next day
        advanced = await self.cog.advance_day(self.channel_id)
        
        if advanced:
            await interaction.response.send_message("Great job! All tasks marked as completed. Moving to the next day.")
        else:
            await interaction.response.send_message("Great job! All tasks marked as completed.")
        
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Show task completion selection
        await interaction.response.send_message("Let's mark the tasks you've completed.")
        
        # Create buttons for each task
        channel_data = self.cog.tasks_data.get(str(self.channel_id), {})
        tasks = channel_data.get("tasks", [])
        
        for task_id in self.today_tasks:
            task = next((t for t in tasks if t["id"] == task_id), None)
            if task:
                view = TaskIndividualCompletionView(self.cog, self.channel_id, task_id)
                await interaction.followup.send(f"Did you complete: {task['name']}?", view=view)
        
        # Add a done button
        view = TaskCompletionDoneView(self.cog, self.channel_id)
        await interaction.followup.send("Click 'Done' when you've marked all tasks.", view=view)
        
        self.stop()

class TaskIndividualCompletionView(View):
    def __init__(self, cog, channel_id, task_id):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.cog = cog
        self.channel_id = channel_id
        self.task_id = task_id

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Mark the task as completed
        channel_data = self.cog.tasks_data.get(str(self.channel_id), {})
        tasks = channel_data.get("tasks", [])
        
        task = next((t for t in tasks if t["id"] == self.task_id), None)
        if task:
            task["completed"] = True
            save_tasks(self.cog.tasks_data)
            
            await interaction.response.send_message(f"Task '{task['name']}' marked as completed.")
        else:
            await interaction.response.send_message("Task not found.")
        
        self.stop()

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Keep the task as not completed
        channel_data = self.cog.tasks_data.get(str(self.channel_id), {})
        tasks = channel_data.get("tasks", [])
        
        task = next((t for t in tasks if t["id"] == self.task_id), None)
        if task:
            task["completed"] = False
            save_tasks(self.cog.tasks_data)
            
            await interaction.response.send_message(f"Task '{task['name']}' marked as not completed.")
        else:
            await interaction.response.send_message("Task not found.")
        
        self.stop()

class TaskCompletionDoneView(View):
    def __init__(self, cog, channel_id):
        super().__init__(timeout=3600)  # 1 hour timeout
        self.cog = cog
        self.channel_id = channel_id

    @discord.ui.button(label="Done", style=discord.ButtonStyle.primary)
    async def done_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Advance to the next day
        advanced = await self.cog.advance_day(self.channel_id)
        
        if advanced:
            await interaction.response.send_message("Moving to the next day.")
        else:
            await interaction.response.send_message("All tasks for today have been reviewed.")
        
        self.stop()

async def setup(bot):
    await bot.add_cog(TaskManagement(bot))