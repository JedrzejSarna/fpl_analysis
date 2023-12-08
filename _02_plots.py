from _01_datasets import *

import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import matplotlib.patches as patches
from IPython.display import display, Image

pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')



class PLOTS(DATASETS):
    def __init__(self):
        super().__init__()
        self.pl_teams_list = [
    ("Arsenal", "#EF0107"),
    ("Aston Villa", "#770A0A"),
    ("Bournemouth", "#DA020E"),
    ("Brentford", "#F20603"),
    ("Brighton", "#0057B8"),
    ("Burnley", "#A52A2A"),
    ("Chelsea", "#034694"),
    ("Crystal Palace", "#E03A3E"),
    ("Everton", "#003399"),
    ("Fulham", "#000000"),
    ("Liverpool", "#C8102E"),
    ("Luton", "#FFA41C"),
    ("Man City", "#6CAEE0"),
    ("Man Utd", "#DA020E"),
    ("Newcastle", "#000000"),
    ("Nott'm Forest", "#DC143C"),
    ("Sheffield Utd", "#EE2737"),
    ("Spurs", "#001C58"),
    ("West Ham", "#7A263A"),
    ("Wolves", "#FFD100"),
]
        
        self.pl_teams = [tup[1] for tup in self.pl_teams_list]
        self.position_teams_dict = {
    "Goalkeeper": "#F1C40F",
    "Defender": "#3498DB",
    "Midfielder": "#27AE60",
    "Forward": "#FF5733"
}
        



    def barplot_fplpoints_per_club(self, df, save = False):
        '''
        Creates barplot displaying sum of fpl points gained per club
        
        Arguments:
            df (pandas.DataFrame) -> dataframe containg fpl points per club
            save (boolean) -> whether the figure should be saved
        Returns:
            plot
        '''        
        fpl_points_per_club = df
        sns.set_style("darkgrid")
        plt.figure(figsize=(15, 6))
        sns.barplot(x=fpl_points_per_club.index, y=fpl_points_per_club.values, palette = self.pl_teams)
        
        plt.xticks(rotation=45, fontsize=12)
        plt.yticks(fontsize=12)
        plt.xlabel('Team', fontsize=15)
        plt.ylabel('Points attained all season', fontsize=15)
        plt.title('Points attained all season for each club', fontsize=18)
        plt.text(0.99, 0.97, "u/DataDrivenDribbler", fontsize=10, ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.5)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/barplot_fplpoints_per_club")
        plt.show()




    def barplot_fplpoints_per_position(self, df, save = False):
        '''creates barplot displaying sum and mean of fpl points gained per position
                
        Arguments:
            df (pandas.DataFrame) -> dataframe containg sum and mean of fpl points gained per position
            save (boolean) -> whether the figure should be saved
        Returns:
            plot
        '''   
        
        sns.set_style("darkgrid")
        plt.figure(figsize=(15, 6))
        sns.barplot(x=df.index, y=df['sum'], palette = list(self.position_teams_dict.values()))

        for i, mean in enumerate(df['mean']):
            plt.annotate(f'Mean for player: {mean:.2f}', (i, mean), xytext=(i-0.34, df['sum'][i]*1.01), fontsize=15)
        for i, count in enumerate(df['count']):
            plt.annotate(f'Count of players: {count}', (i, count), xytext=(i-0.34, 75), fontsize=15)
        
        plt.xticks(rotation=45, fontsize=15)
        plt.yticks(fontsize=12)
        plt.xlabel('Positions', fontsize=18)
        plt.ylabel('Points attained all season', fontsize=18)
        plt.title('Points attained all season per position', fontsize=20)
        plt.text(0.99, 0.97, "u/DataDrivenDribbler", fontsize=10, ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.5)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/barplot_fplpoints_per_position")
        plt.show()

 
    def scatterplot_Goals_vs_xG(self, df, save=False):
        '''Creates scatterplot displaying goals vs expected goals for each club
              
        Arguments:
            df (pandas.DataFrame) -> dataframe containing sum of goals and xG per club
            save (boolean) -> whether the figure should be saved
        Returns:
            plot
        '''   
        
        sns.set_style("white")
        plt.figure(figsize=(20, 8))

        sns.scatterplot(x=df['goals_scored'].values, y=df['expected_goals'].values, s = 200, c = self.pl_teams)

        for index, club in enumerate(df['goals_scored'].index):
            plt.text(df['goals_scored'][index]-0.3, df['expected_goals'][index]+0.25, club, fontsize = 12)

        x_values = np.linspace(0, max(max(df['goals_scored'].values),max(df['expected_goals'].values))+1)
        plt.plot(x_values, x_values, color='gray', linestyle='--')

        overperform_area = [(0, 0), (max(df['goals_scored'].values)+1, 0), (max(df['goals_scored'].values)+1, max(df['goals_scored'].values)+1)]
        overperform_triangle = patches.Polygon(overperform_area, closed=True, facecolor='lightgreen', alpha=0.2)

        underperform_area = [(0, 0), (0, max(df['goals_scored'].values)+1), (max(df['goals_scored'].values)+1, max(df['goals_scored'].values)+1)]
        underperform_triangle = patches.Polygon(underperform_area, closed=True, facecolor='lightcoral', alpha=0.2)
        
        ax = plt.gca()
        ax.add_patch(overperform_triangle)
        ax.add_patch(underperform_triangle)

        plt.text(1, max(df['expected_goals'].values)-1, 'UNDERPERFORMING', fontsize = 20, c = 'salmon')
        plt.text(max(df['goals_scored'].values)*0.8,1, 'OVERPERFORMING', fontsize = 20, c= 'mediumseagreen')


        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Goals', fontsize=18)
        plt.ylabel('Expected Goals', fontsize=18)
        plt.title('Goals vs Expected Goals (without OG)', fontsize=20)
        plt.xlim(0, max(df['goals_scored'].values)+1)
        plt.ylim(0, max(df['expected_goals'].values)+1)
        plt.annotate("u/DataDrivenDribbler", xy=(max(df['goals_scored'].values)*0.93, 0.05), fontsize=10, alpha=0.5)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/scatterplot_Goals_vs_xG")
        plt.show()




    def scatterplot_Goals_Against_vs_xGA(self, df, save=False):
        '''Creates scatterplot displaying goals against vs expected goals against for each club
              
        Arguments:
            df (pandas.DataFrame) -> dataframe containg sum of goals against and xGA per club
            save (boolean) -> whether the figure should be saved
        Returns:
            plot
        '''   
        
        sns.set_style("white")
        plt.figure(figsize=(20, 8))

        sns.scatterplot(x=df['goals_conceded'].values, y=df['expected_goals_conceded'].values, s = 200, c = self.pl_teams)

        for index, club in enumerate(df['goals_conceded'].index):
            plt.text(df['goals_conceded'][index]-0.3, df['expected_goals_conceded'][index]+0.25, club, fontsize = 12)

        x_values = np.linspace(0, max(max(df['goals_conceded'].values),max(df['expected_goals_conceded'].values))+1)
        plt.plot(x_values, x_values, color='gray', linestyle='--')


        underperform_area = [(0, 0), (max(df['goals_conceded'].values)+1, 0), (max(df['goals_conceded'].values)+1, max(df['goals_conceded'].values)+1)]
        underperform_triangle = patches.Polygon(underperform_area, closed=True, facecolor='lightcoral', alpha=0.2)

        overperform_area = [(0, 0), (0, max(df['expected_goals_conceded'].values)+1), (max(df['expected_goals_conceded'].values)+1, max(df['expected_goals_conceded'].values)+1)]
        overperform_triangle = patches.Polygon(overperform_area, closed=True, facecolor='lightgreen', alpha=0.2)
        
        ax = plt.gca()
        ax.add_patch(overperform_triangle)
        ax.add_patch(underperform_triangle)

        plt.text(1, max(df['expected_goals_conceded'].values)-1, 'OVERPERFORMING', fontsize = 20, c = 'mediumseagreen')
        plt.text(max(df['goals_conceded'].values)*0.8,1, 'UNDERPERFORMING', fontsize = 20, c= 'salmon')


        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Goals Against', fontsize=18)
        plt.ylabel('Expected Goals Against', fontsize=18)
        plt.title('Goals Against vs Expected Goals Against', fontsize=20)
        plt.xlim(0, max(df['goals_conceded'].values)+1)
        plt.ylim(0, max(df['expected_goals_conceded'].values)+1)
        plt.annotate("u/DataDrivenDribbler", xy=(max(df['goals_conceded'].values)*0.93, 0.05), fontsize=10, alpha=0.5)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/scatterplot_Goals_Against_vs_xGA")
        plt.show()
        



    def barplot_fplpoints_split(self, df, save = False):
        '''Creates barplot displaying split of fpl points for the season
              
        Arguments:
            df (pandas.DataFrame) -> dataframe containg percentage of each category
            save (boolean) -> whether the figure should be saved
        Returns:
            plot
        '''   
        
        sns.set_style("darkgrid")
        sns.color_palette("coolwarm", as_cmap=True)
        plt.figure(figsize=(20, 8))
        sns.set(font_scale=2)


        sns.barplot(x=df['Action'], y=df['Percentage (%)'], palette = 'coolwarm')

        for i, pct in enumerate(df['Percentage (%)']):
            plt.annotate(f'{pct:.2f}%', (i, pct), ha='center', va='bottom', fontsize=15)

        plt.ylim(min(df['Percentage (%)']) - 1, max(df['Percentage (%)']) + 1)
        plt.xticks(fontsize=13)
        plt.yticks([i for i in range(-10,51,10)], fontsize=13)
        plt.title('(Approximate) Split of total FPL points per action', fontsize=24)
        plt.text(0.99, 0.97, "u/DataDrivenDribbler", fontsize=10, ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.5)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/barplot_fplpoints_split")
        plt.show()
    
    def pointplot_best_player_per_team_points(self, df, save=False):

        sns.set_style("darkgrid")
        plt.figure(figsize=(20, 8))
        for ind, player in enumerate(df.columns):
            sns.lineplot(x=df.index, y=df[player], marker='o', color = self.pl_teams[ind])

        plt.xticks(np.arange(min(df.index), max(df.index)+1, 1.0), fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Gameweek', fontsize=18)
        plt.ylabel('Total points', fontsize=18)
        plt.title('Track of points for best player per team', fontsize=20)
        
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in self.pl_teams]
        plt.legend(legend_handles, df.columns, loc='upper left', ncols=2, fontsize=12)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/pointplot_best_player_per_team_points")
        plt.show()

    def pointplot_top5_player_points(self, df, save=False):

        self.build_players_dataset()
        self.build_positions_dataset()
        self.build_teams_dataset()
        self.transform_players_dataset()
        teams=[]
        for name in df.columns:
            teams.append(self.players_dataset.loc[self.players_dataset['player_name']==name, 'team_name'].values[0])
        colors=[]
        for team in teams:
            for team_code in self.pl_teams_list:
                if team == team_code[0]:
                    colors.append(team_code[1])

        sns.set_style("darkgrid")
        plt.figure(figsize=(20, 8))
        for ind, player in enumerate(df.columns):
            sns.lineplot(x=df.index, y=df[player], marker='o', color = colors[ind])

        plt.xticks(np.arange(min(df.index), max(df.index)+1, 1.0), fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Gameweek', fontsize=18)
        plt.ylabel('Total points', fontsize=18)
        plt.title('Points evolution for Top 5 players (one per team)', fontsize=20)
        
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in colors]
        plt.legend(legend_handles, df.columns, loc='upper left', ncols=2, fontsize=12)
        plt.text(0.99, 0.03, "u/DataDrivenDribbler", fontsize=10, ha='right', va='bottom', transform=plt.gca().transAxes, alpha=0.5)

        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/pointplot_top5_player_points")
        plt.show()

    
    def pointplot_top5_defender_points(self, df, save=False):
                
        self.build_players_dataset()
        self.build_positions_dataset()
        self.build_teams_dataset()
        self.transform_players_dataset()
        teams=[]
        for name in df.columns:
            teams.append(self.players_dataset.loc[self.players_dataset['player_name']==name, 'team_name'].values[0])
        colors=[]
        for team in teams:
            for team_code in self.pl_teams_list:
                if team == team_code[0]:
                    colors.append(team_code[1])

        sns.set_style("darkgrid")
        plt.figure(figsize=(20, 8))
        for ind, player in enumerate(df.columns):
            sns.lineplot(x=df.index, y=df[player], marker='o', color = colors[ind])

        plt.xticks(np.arange(min(df.index), max(df.index)+1, 1.0), fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Gameweek', fontsize=18)
        plt.ylabel('Total points', fontsize=18)
        plt.title('Points evolution for Top 5 defenders (one per team)', fontsize=20)
        
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in colors]
        plt.legend(legend_handles, df.columns, loc='upper left', ncols=2, fontsize=12)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/pointplot_top5_defender_points")
        plt.show()


    
    def pointplot_top5_midfielder_points(self, df, save=False):
                
        self.build_players_dataset()
        self.build_positions_dataset()
        self.build_teams_dataset()
        self.transform_players_dataset()
        teams=[]
        for name in df.columns:
            teams.append(self.players_dataset.loc[self.players_dataset['player_name']==name, 'team_name'].values[0])
        colors=[]
        for team in teams:
            for team_code in self.pl_teams_list:
                if team == team_code[0]:
                    colors.append(team_code[1])

        sns.set_style("darkgrid")
        plt.figure(figsize=(20, 8))
        for ind, player in enumerate(df.columns):
            sns.lineplot(x=df.index, y=df[player], marker='o', color = colors[ind])

        plt.xticks(np.arange(min(df.index), max(df.index)+1, 1.0), fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Gameweek', fontsize=18)
        plt.ylabel('Total points', fontsize=18)
        plt.title('Points evolution for Top 5 midfielders (one per team)', fontsize=20)
        
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in colors]
        plt.legend(legend_handles, df.columns, loc='upper left', ncols=2, fontsize=12)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/pointplot_top5_midfielder_points")
        plt.show()

    
    def pointplot_top5_forward_points(self, df, save=False):
                
        self.build_players_dataset()
        self.build_positions_dataset()
        self.build_teams_dataset()
        self.transform_players_dataset()
        teams=[]
        for name in df.columns:
            teams.append(self.players_dataset.loc[self.players_dataset['player_name']==name, 'team_name'].values[0])
        colors=[]
        for team in teams:
            for team_code in self.pl_teams_list:
                if team == team_code[0]:
                    colors.append(team_code[1])

        sns.set_style("darkgrid")
        plt.figure(figsize=(20, 8))
        for ind, player in enumerate(df.columns):
            sns.lineplot(x=df.index, y=df[player], marker='o', color = colors[ind])

        plt.xticks(np.arange(min(df.index), max(df.index)+1, 1.0), fontsize=14)
        plt.yticks(fontsize=14)
        plt.xlabel('Gameweek', fontsize=18)
        plt.ylabel('Total points', fontsize=18)
        plt.title('Points evolution for Top 5 forwards (one per team)', fontsize=20)
        
        legend_handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, markersize=10) for color in colors]
        plt.legend(legend_handles, df.columns, loc='upper left', ncols=2, fontsize=12)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/pointplot_top5_forward_points")
        plt.show()

        
    def barplot_top5_overperformers(self, df, save=False):
        df_top5 = df.head()

        plt.figure(figsize=(15, 6))        
        sns.barplot(x=df_top5["player_name"], y=df_top5["goal_involvements"], color='lightsteelblue')
        sns.barplot(x=df_top5["player_name"], y=df_top5["expected_goal_involvements"], color='midnightblue')

        for i, entry in enumerate(df_top5['goal_involvements']):
            plt.annotate(f"Goal involvements: {entry}", (i, entry), xytext=(i-0.34, entry*1.01), fontsize=10)
        for i, entry in enumerate(df_top5['expected_goal_involvements']):
            plt.annotate(f"XG involvements: {entry}", (i, entry), xytext=(i-0.34, entry*1.01), fontsize=10)
        plt.xlabel('Player', fontsize=18)
        plt.ylabel('Goals', fontsize=18)
        plt.title('Biggest overperformers (XGI - XG difference)', fontsize=20)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/barplot_top5_overperformers")
        plt.show()

    def barplot_top5_underperformers(self, df, save=False):
        df_top5 = df.iloc[-5:]

        plt.figure(figsize=(15, 6))
        sns.barplot(x=df_top5["player_name"], y=df_top5["expected_goal_involvements"], color='lightcoral')
        sns.barplot(x=df_top5["player_name"], y=df_top5["goal_involvements"], color='darkred')

        for i, entry in enumerate(df_top5['goal_involvements']):
            plt.annotate(f"Goal involvements: {entry}", (i, entry), xytext=(i-0.34, entry*1.01), fontsize=10)
        for i, entry in enumerate(df_top5['expected_goal_involvements']):
            plt.annotate(f"XG involvements: {entry}", (i, entry), xytext=(i-0.34, entry*1.01), fontsize=10)
        plt.xlabel('Player', fontsize=18)
        plt.ylabel('Goals', fontsize=18)
        plt.title('Biggest underperformers (XGI - XG difference)', fontsize=20)
        if save == True:       
            plt.savefig("/Users/jedrzejsarna/Desktop/GitHub/fpl_analysis/figures/barplot_top5_underperformers")
        plt.show()      
