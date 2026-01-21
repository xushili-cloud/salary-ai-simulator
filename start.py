import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        user_data_dir = "./boss_data"
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        page = context.pages[0]
        
        try:
            print("🚀 正在前往 BOSS 直聘...")
            await page.goto("https://www.zhipin.com/web/geek/job?query=AI产品经理&city=101010100") 
            
            print("\n⚠️  重要提示：")
            print("1. 请确保浏览器窗口【一直开启】，不要关闭它。")
            print("2. 如果有验证码，请手动完成。")
            print("3. 看到职位列表后，回到这里按回车。")
            
            input("👉 确认看到职位列表了吗？按回车开始抓取：")

            # 检查页面是否还活着
            if page.is_closed():
                print("❌ 错误：浏览器窗口已被关闭，无法抓取。")
                return

            print("🔍 正在提取职位信息...")
            # 给网页一点点缓冲时间
            await page.wait_for_timeout(2000)

            # 尝试几种常见的选择器
            selectors = [".job-card-wrapper", ".job-card-box", ".job-list-box li"]
            job_cards = []
            
            for selector in selectors:
                job_cards = await page.locator(selector).all()
                if len(job_cards) > 0:
                    print(f"🎯 匹配成功，使用选择器: {selector}")
                    break

            jobs_list = []
            for card in job_cards:
                try:
                    # 获取文本时增加判断
                    title = await card.locator(".job-name").inner_text()
                    salary = await card.locator(".salary").inner_text()
                    company = await card.locator(".company-name").inner_text()
                    
                    job_info = f"职位: {title} | 薪资: {salary} | 公司: {company}"
                    jobs_list.append(job_info)
                    print(f"✅ 已抓取: {title}")
                except:
                    continue

            if jobs_list:
                with open("boss_raw_data.txt", "w", encoding="utf-8") as f:
                    for item in jobs_list:
                        f.write(item + "\n")
                print(f"\n🎉 成功！已抓取 {len(jobs_list)} 条数据。")
            else:
                print("\n😅 没抓到数据，请检查搜索结果是否为空。")

        except Exception as e:
            print(f"\n❌ 运行中出现意外: {e}")
        finally:
            # 无论是否成功，最后都尝试关闭，除非已经关了
            if not page.is_closed():
                await context.close()

if __name__ == "__main__":
    asyncio.run(run())