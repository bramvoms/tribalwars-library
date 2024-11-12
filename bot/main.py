class SearchModal(Modal):
    def __init__(self, bot):
        super().__init__(title="Search Scripts")
        self.bot = bot
        self.query = TextInput(label="Enter script name or keyword", placeholder="e.g., Offpack")
        self.add_item(self.query)

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query.value.lower()
        results = []

        # Step 1: Exact match check
        if query in descriptions:
            results.append((query, descriptions[query]))
        else:
            # Step 2: Advanced matching with substring and fuzzy matching
            matches = []
            for subcategory, description in descriptions.items():
                subcategory_lower = subcategory.lower()
                description_lower = description.lower()
                
                # Direct substring match
                if query in subcategory_lower or query in description_lower:
                    matches.append((subcategory, description, 90))  # High priority for direct substring matches

                # Fuzzy match with a lower threshold for partial and token set ratios
                elif (fuzz.partial_ratio(query, subcategory_lower) > 50 or fuzz.token_set_ratio(query, subcategory_lower) > 50):
                    score = max(fuzz.partial_ratio(query, subcategory_lower), fuzz.token_set_ratio(query, subcategory_lower))
                    matches.append((subcategory, description, score))  # Priority based on fuzzy score

            # Sort matches by score to prioritize closer matches
            matches = sorted(matches, key=lambda x: x[2], reverse=True)

            # Remove duplicates and keep only the subcategory and description fields
            results = [(subcategory, description) for subcategory, description, _ in dict.fromkeys(matches)]

        # Limit the output to the top 2 results
        top_results = results[:2]

        # Determine the best suggestion not in top 2 results, if available
        suggestion = results[2] if len(results) > 2 else None

        # Create the view with top results and a "Did you mean..." button if there’s a suggestion
        view = ResultSelectionView(top_results, suggestion)

        await interaction.response.send_message(
            content="Select the script you want more details about:",
            view=view,
            ephemeral=True
        )


class ResultSelectionView(View):
    def __init__(self, results, suggestion=None):
        super().__init__()
        self.results = results
        self.suggestion = suggestion
        self.add_result_selector()

        # Add "Did you mean..." button if there's a suggestion
        if self.suggestion:
            self.add_suggestion_button()

    def add_result_selector(self):
        # Limit descriptions to 100 characters
        options = [
            discord.SelectOption(label=subcategory, description=(description[:97] + "..." if len(description) > 100 else description))
            for subcategory, description in self.results
        ]
        select = Select(placeholder="Choose a script...", options=options)
        select.callback = self.show_description
        self.add_item(select)

    def add_suggestion_button(self):
        suggestion_button = Button(label=f"Did you mean '{self.suggestion[0]}'?", style=discord.ButtonStyle.secondary)
        suggestion_button.callback = self.show_suggestion
        self.add_item(suggestion_button)

    async def show_description(self, interaction: discord.Interaction):
        selected_script = interaction.data["values"][0]
        description = descriptions.get(selected_script, "No description available.")
        await interaction.response.send_message(f"**{selected_script}**:\n{description}", ephemeral=True)

    async def show_suggestion(self, interaction: discord.Interaction):
        suggested_script, suggested_description = self.suggestion
        await interaction.response.send_message(f"**{suggested_script}**:\n{suggested_description}", ephemeral=True)
