import sys

# 校园双模式导航（赚钱版：步行+驾车+商家广告）
class CampusNav:
    def __init__(self):
        self.INF = float('inf')
        # 地点列表（含广告商家）
        self.places = [
            "南门", "办公楼", "教学楼A", "教学楼B",
            "食堂", "图书馆", "学生宿舍", "停车场",
            "🍵蜜雪冰城（广告）", "🖨️学霸打印店（广告）"  # 赚钱点位
        ]
        self.n = len(self.places)

        # 步行图（可走小路、捷径）
        self.walk_graph = [[self.INF] * self.n for _ in range(self.n)]
        # 驾车图（仅车道，禁行区不通）
        self.car_graph = [[self.INF] * self.n for _ in range(self.n)]

        for i in range(self.n):
            self.walk_graph[i][i] = 0
            self.car_graph[i][i] = 0

        self.init_map()

    # 初始化路径
    def init_map(self):
        # 步行路径
        self.add_edge(self.walk_graph, 0, 1, 150)
        self.add_edge(self.walk_graph, 0, 6, 200)
        self.add_edge(self.walk_graph, 1, 2, 80)
        self.add_edge(self.walk_graph, 2, 3, 100)
        self.add_edge(self.walk_graph, 3, 4, 90)
        self.add_edge(self.walk_graph, 4, 5, 70)
        self.add_edge(self.walk_graph, 5, 6, 120)
        self.add_edge(self.walk_graph, 6, 8, 50)   # 宿舍→奶茶店
        self.add_edge(self.walk_graph, 2, 9, 60)   # 教学楼→打印店

        # 驾车路径（宿舍、教学楼内部禁行）
        self.add_edge(self.car_graph, 0, 1, 300)
        self.add_edge(self.car_graph, 1, 7, 200)
        self.add_edge(self.car_graph, 0, 7, 400)
        self.add_edge(self.car_graph, 1, 8, 200)  # 办公楼→奶茶店
        self.add_edge(self.car_graph, 7, 9, 180)  # 停车场→打印店

    def add_edge(self, graph, a, b, w):
        graph[a][b] = w
        graph[b][a] = w

    # Dijkstra 核心算法
    def dijkstra(self, graph, start, end):
        dist = [self.INF] * self.n
        pre = [-1] * self.n
        vis = [False] * self.n
        dist[start] = 0

        for _ in range(self.n):
            min_dist = self.INF
            u = -1
            for i in range(self.n):
                if not vis[i] and dist[i] < min_dist:
                    min_dist = dist[i]
                    u = i
            if u == -1:
                break
            vis[u] = True
            for v in range(self.n):
                if not vis[v] and graph[u][v] != self.INF:
                    if dist[v] > dist[u] + graph[u][v]:
                        dist[v] = dist[u] + graph[u][v]
                        pre[v] = u

        if dist[end] == self.INF:
            print("❌ 无法到达该地点")
            return

        print(f"✅ 最短距离：{dist[end]} 米")
        print("🚗 推荐路线：", end="")
        self.print_path(pre, end)
        print()

        # ======================
        # 赚钱模块：商家广告
        # ======================
        self.show_ad(end)

    # 递归打印路径
    def print_path(self, pre, v):
        if pre[v] == -1:
            print(self.places[v], end="")
            return
        self.print_path(pre, pre[v])
        print(f" → {self.places[v]}", end="")

    # 智能广告推荐（赚钱核心）
    def show_ad(self, end):
        print("\n📢 附近商家推荐：")
        if end in [2, 3]:  # 教学楼
            print("👉 学霸打印店：打印复印8折，导航到店立减1元")
        elif end in [6, 4]:  # 宿舍/食堂
            print("👉 蜜雪冰城：第二杯半价，凭导航截图优惠")
        elif end in [1, 7]:  # 办公楼/停车场
            print("👉 校内便利店：满20减5，领导访客专享")
        else:
            print("👉 全店通用：导航到店即可享受专属优惠")

    # 显示地点菜单
    def show_places(self):
        print("\n===== 校园地点 =====")
        for i, name in enumerate(self.places):
            print(f"{i}：{name}")

    # 启动导航
    def start(self):
        print("=" * 40)
        print("     🏫 校园智能导航系统（赚钱版）")
        print("=" * 40)
        print("1 👨‍🎓 新生/学生 → 步行导航")
        print("2 👔 领导/访客 → 驾车导航")

        try:
            mode = int(input("\n请选择模式（1/2）："))
            self.show_places()
            start = int(input("请输入起点编号："))
            end = int(input("请输入终点编号："))

            if mode == 1:
                print("\n————【步行模式】————")
                self.dijkstra(self.walk_graph, start, end)
            elif mode == 2:
                print("\n————【驾车模式】————")
                self.dijkstra(self.car_graph, start, end)
            else:
                print("输入错误！")
        except:
            print("输入无效！")

if __name__ == "__main__":
    nav = CampusNav()
    nav.start()