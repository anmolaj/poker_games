import json
from typing import Dict

import requests
import logging

import yaml

logging.basicConfig(level=logging.INFO)


class PokerBalance:
	def __init__(self, pokernow_url: str):
		self.play_url = f"{pokernow_url}/players_sessions"
		self.mapping_file = "player_mapping.yaml"
		logging.info(f"Hitting URL {self.play_url}")
		self.name_mapping: Dict = {}
		self.new_players = {}
		self.set_player_mapping()

	def set_player_mapping(self):
		name_mapping = {}
		with open(self.mapping_file, "r") as f:
			self.yml = yaml.safe_load(f)
			for player, values in self.yml.items():
				for name in values["names"]:
					name_mapping[name] = player
		self.name_mapping = name_mapping

	def get_end_stats(self):
		r = requests.get(self.play_url)
		play_session = json.loads(r.text)
		end_player_stats = {}
		for _id, player_info in play_session["playersInfos"].items():
			player = player_info["names"][0]
			if player not in self.name_mapping:
				print(F"Player {player} might be new player please add it")
				print(F"Existing names {self.name_mapping.keys()}")
				player_og_name = input(F"Enter mapping for {player}: ")
				self.new_players[player_og_name] = self.new_players.get(player_og_name, []) + [player]
			player_og_name = self.name_mapping[player]

			end_player_stats[player_og_name] = round(player_info["net"] / 10.0 + \
											   end_player_stats.get(player_og_name, 0),1)
			print(F" {end_player_stats[player_og_name]}, {round(player_info['net'] / 10.0, 1)}")
		return end_player_stats

	def set_new_player_mapping(self):
		if len(self.new_players) == 0:
			logging.info("No new players")
			return
		logging.info(f'Adding {len(self.new_players)} players')
		for player, names in self.new_players.items():
			self.yml[player] = self.yml.get(player, {'names': []})
			self.yml[player]["names"] = self.yml[player]["names"] + names

		with open(self.mapping_file, 'w') as file:
			yaml.dump(self.yml, file)


if __name__ == '__main__':
	url = input("Enter URL: ")
	pp = PokerBalance(url)
	print(pp.get_end_stats())
	pp.set_new_player_mapping()
