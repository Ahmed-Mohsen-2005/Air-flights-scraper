import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
from serpapi import GoogleSearch
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import numpy as np
import networkx as nx
import cv2
import math
import random
def main_app():
    root = tk.Tk()
    root.title("Air Flights Scraper")
    root.geometry("1000x600")
    splash_image = Image.open("plane.jpg")
    splash_photo = ImageTk.PhotoImage(splash_image)
    splash_label = tk.Label(root, image=splash_photo)
    splash_label.pack(fill='both', expand=True)
    welcome_text = tk.Label(root, text="Welcome to your Air Flights Scraper", font=("QT ", 24), bg="#000000", fg="white")
    welcome_text.place(relx=0.5, rely=0.5, anchor='center')

    tabControl = ttk.Notebook(root)

    tabs = ['Home', 'Web Scraping', 'Network Implementation', 'Network Analysis', 'Heatmap', '3D Modelling']
    tab_frames = {}
    tab_backgrounds = {
        'Web Scraping': 'web scraping.jpg',
        'Network Implementation': 'network.jpg',
        'Network Analysis': 'network analysis.jpg',
        'Heatmap': 'heatmap.jpg',
        '3D Modelling': '3d model.jpg'
    }

    def setup_home_tab():
        home_image = Image.open("home.jpg")
        home_photo = ImageTk.PhotoImage(home_image)
        home_background_label = tk.Label(tab_frames['Home'], image=home_photo)
        home_background_label.image = home_photo
        home_background_label.place(x=0, y=0, relwidth=1, relheight=1)

        for tab in tabs[1:]:  # Skip the 'Home' tab itself
            btn = ttk.Button(tab_frames['Home'], text=tab, command=lambda t=tab: show_tab(t))
            btn.pack(pady=10, padx=10)

    def show_tab(tab):
        tabControl.select(tab_frames[tab])

    def set_tab_background(tab_frame, image_path):
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)
        background_label = tk.Label(tab_frame, image=photo)
        background_label.image = photo
        background_label.place(x=0, y=0, relwidth=1, relheight=1)

    source = []
    destination = []

    for tab in tabs:
        tab_frames[tab] = ttk.Frame(tabControl)
        tabControl.add(tab_frames[tab], text=tab)
        if tab != 'Home':
            set_tab_background(tab_frames[tab], tab_backgrounds.get(tab, 'default.jpg'))
        if tab == 'Web Scraping':
            def perform_scraping():
                nonlocal source, destination
                source.clear()
                destination.clear()

                api_key = '1724f7601632717a495558b4e65b6869e6e6561665b1dbe5ac39b871fd8f9a36'
                query = 'openflights flights routes'
                search = GoogleSearch({"q": query, "api_key": api_key})
                results = search.get_dict()

                datasets = []
                for result in results['organic_results']:
                    dataset_name = result['title']
                    dataset_url = result['link']
                    datasets.append({'name': dataset_name, 'url': dataset_url})

                dataset_index = 1
                mylink = datasets[dataset_index]['url']
                r = requests.get(mylink)
                x = BeautifulSoup(r.content, "html.parser")

                results = x.find_all("a")
                dat_files = []
                for link in results:
                    if link.has_attr('href'):
                        href = link['href']
                        if href.endswith("dat"):
                            dat_files.append(href)
                dataset_link = dat_files[5]
                m = requests.get(dataset_link)
                data = BeautifulSoup(m.content, "html.parser")
                lines = data.text.splitlines()
                data_list = []
                for line in lines:
                    line = line.split(",")
                    data_list.append(line)

                for l in data_list:
                    source.append(l[2])
                    destination.append(l[4])

                sources = source[:100]
                destinations = destination[:100]

                output_text = "Web Scraping Results:\n"
                for dataset in datasets:
                    output_text += str(dataset['name']) + ": " + str(dataset['url']) + "\n"
                output_text += f"\nMy website link is: {mylink}\n"
                output_text += f"Found {len(dat_files)} .dat files\n"
                output_text += "List of .dat files:\n" + "\n".join(dat_files)
                output_text += "\n\nMy dataset link is: " + dataset_link
                output_text += "\n" + str(m)
                output_text += "\n\nSources: " + str(sources)
                output_text += "\n\nDestinations: " + str(destinations)

                display_output.delete('1.0', tk.END)
                display_output.insert(tk.END, output_text)
                return sources, destinations

            scrape_btn = ttk.Button(tab_frames['Web Scraping'], text="Show scrapped results by SerpAPI",
                                    command=perform_scraping)
            scrape_btn.pack(pady=10)
            display_output = scrolledtext.ScrolledText(tab_frames['Web Scraping'],width=30, height=10)
            display_output.pack(fill=tk.BOTH, expand=True)
        elif tab == 'Network Implementation':
            def show_network_drawing(flight_data):
                nonlocal source, destination
                G = nx.DiGraph()
                for src, dst in zip(flight_data[0], flight_data[1]):
                    G.add_edge(src, dst)
                pos = nx.spring_layout(G)
                plt.figure(figsize=(10, 10))
                nx.draw(G, pos, with_labels=True, node_size=200, font_size=7, font_color="w")
                plt.show()

            network_btn = ttk.Button(tab_frames['Network Implementation'], text="Show the network drawing",
                                     command=lambda: show_network_drawing(perform_scraping()))
            network_btn.pack(pady=10)
        elif tab == 'Network Analysis':
            def show_network_analysis(flight_data):
                nonlocal source, destination
                G = nx.DiGraph()
                for src, dst in zip(flight_data[0], flight_data[1]):
                    G.add_edge(src, dst)

                # Display degrees
                degree_text = "Nodes degrees:\n"
                for i in G.nodes:
                    d = G.degree[i]
                    degree_text += f"Node {i}: >>>>>>> {d}\n"

                false_betweenness = nx.betweenness_centrality(G, normalized=False)
                false_values = list(false_betweenness.values())
                false_max = max(false_values) if false_values else 0
                betweenness_text = "Betweenness with false normalization: " + str(false_betweenness) + "\n"
                betweenness_text += "Max: " + str(false_max) + "\n"

                # Calculate betweenness with true normalization
                true_betweenness = nx.betweenness_centrality(G)
                true_values = list(true_betweenness.values())
                true_max = max(true_values) if true_values else 0
                true_index = true_values.index(true_max) if true_values else 0
                max_true_node = max(true_betweenness, default='N/A')
                betweenness_text += "Betweenness with true normalization: " + str(true_betweenness) + "\n"
                betweenness_text += "Max: " + str(true_max) + "\n"
                betweenness_text += "\nBetweenness index: " + str(true_index) + "\n"
                betweenness_text += f"The most important airport (from number of landings) is {max_true_node}"

                # Display the results
                analysis_output.delete('1.0', tk.END)
                analysis_output.insert(tk.END, degree_text + betweenness_text)

            analysis_btn = ttk.Button(tab_frames['Network Analysis'], text="Show degree and betweenness",
                                      command=lambda: show_network_analysis(perform_scraping()))
            analysis_btn.pack(pady=10)
            analysis_output = scrolledtext.ScrolledText(tab_frames['Network Analysis'], width=30, height=10)
            analysis_output.pack(fill=tk.BOTH, expand=True)
        elif tab == '3D Modelling':
            def show_3d_model(flight_data):
                nonlocal source, destination
                G = nx.DiGraph()
                for src, dst in zip(flight_data[0], flight_data[1]):
                    G.add_edge(src, dst)

                fig = plt.figure(figsize=(15, 12))
                ax = fig.add_subplot(111, projection='3d')

                pos = nx.spring_layout(G, dim=3)
                for node, (x, y, z) in pos.items():
                    ax.scatter(x, y, z, label=node)

                for edge in G.edges():
                    ax.plot([pos[edge[0]][0], pos[edge[1]][0]],
                            [pos[edge[0]][1], pos[edge[1]][1]],
                            [pos[edge[0]][2], pos[edge[1]][2]])

                ax.set_xlabel('X')
                ax.set_ylabel('Y')
                ax.set_zlabel('Z')
                ax.set_title("The 3D model of the network")
                # plt.legend()
                plt.show()

            model_btn = ttk.Button(tab_frames['3D Modelling'], text="Show 3D model",
                                   command=lambda: show_3d_model(perform_scraping()))
            model_btn.pack(pady=10)

        elif tab == 'Heatmap':
            def show_heatmap():
                nonlocal source, destination
                G = nx.DiGraph()

                xs = []
                ys = []
                for i in range(100):
                    x = random.randint(400, 430)
                    xs.append(x)
                    y = random.randint(845, 875)
                    ys.append(y)

                grid_size = 1
                h = 10
                x_min = min(xs)
                x_max = max(xs)
                y_min = min(ys)
                y_max = max(ys)
                x_grid = np.arange(x_min - h, x_max + h, grid_size)
                y_grid = np.arange(y_min - h, y_max + h, grid_size)
                x_mesh, y_mesh = np.meshgrid(x_grid, y_grid)
                xc = x_mesh + (grid_size / 2)
                yc = y_mesh + (grid_size / 2)

                intensity_list = []
                for r in range(len(xc)):
                    intensity_row = []
                    for c in range(len(xc[0])):
                        kde_value_list = []
                        for i in range(len(xs)):
                            d = math.sqrt((xc[r][c] - xs[i]) ** 2 + (yc[r][c] - ys[i]) ** 2)
                            if d <= h:
                                p = kde_quartic(d, h)
                            else:
                                p = 0
                            kde_value_list.append(p)
                        p_total = sum(kde_value_list)
                        intensity_row.append(p_total)
                    intensity_list.append(intensity_row)
                intensity = np.array(intensity_list)

                plt.pcolormesh(x_mesh, y_mesh, intensity)
                plt.plot(xs, ys, 'ro')
                # plt.colorbar()
                fig1 = plt.gcf()
                plt.axis("off")
                plt.show()
                plt.draw()
                fig1.savefig("hmap.jpg")
                S1 = cv2.imread('hmap.jpg')
                S2 = cv2.imread('world.bmp')
                S2 = cv2.cvtColor(S2, cv2.COLOR_BGR2RGB)
                # plt.imshow(S2)

                S22 = cv2.resize(S2, (S1.shape[1], S1.shape[0]), interpolation=cv2.INTER_AREA)
                alpha = 0.7
                image_new = cv2.addWeighted(S1, alpha, S22, 1 - alpha, 0)
                plt.imshow(image_new)
                plt.axis("off")

                # plt.imshow(S1)
                plt.show()

            def kde_quartic(d, h):
                dn = d / h
                P = (15 / 16) * (1 - dn ** 2) ** 2
                return P

            heatmap_btn = ttk.Button(tab_frames['Heatmap'], text="Show heatmap",
                                     command=show_heatmap)
            heatmap_btn.pack(pady=10)

    def show_main_app():
        splash_label.pack_forget()
        welcome_text.pack_forget()
        setup_home_tab()
        tabControl.pack(expand=1, fill="both")

    root.after(4000, show_main_app)

    root.mainloop()

if __name__ == "__main__":
    main_app()