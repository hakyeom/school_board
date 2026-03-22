import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os

async def get_unanswered_posts():
    """
    운암중학교 질문답변 게시판에 로그인하여 답변 대기 상태인 게시글을 스크래핑합니다.
    """
    scraped_data = []
    print("스크래핑 프로세스를 시작합니다.")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # 1. 정확한 로그인 페이지 주소로 접속
            login_url = "http://unam.gen.ms.kr/login.php?id=94"
            print(f"로그인 페이지({login_url})로 이동합니다...")
            await page.goto(login_url, wait_until="networkidle")
            print("로그인 페이지 로드 완료.");

            # 2. 올바른 선택자로 아이디와 비밀번호 입력
            user_id = "multiclass1"
            user_pw = "multi12345!"

            print("아이디와 비밀번호를 입력합니다...")
            await page.locator('input[name="userid"]').fill(user_id)
            await page.locator('input[name="passwd"]').fill(user_pw)
            print("아이디/비밀번호 입력 완료.");

            # 3. 로그인 버튼 클릭
            print("로그인 버튼을 클릭합니다...")
            async with page.expect_navigation():
                await page.locator('button[type="submit"]').click()
            print("로그인 성공. 다음 페이지로 이동합니다.");

            # 4. 질문답변 게시판으로 이동
            # 참고: id=81은 '고장신고' 게시판입니다. 원래 요청대로 진행합니다.
            qna_board_url = "http://unam.gen.ms.kr/board.php?id=81"
            print(f"질문답변(고장신고) 게시판({qna_board_url})으로 이동합니다.")
            await page.goto(qna_board_url, wait_until="networkidle")
            print("게시판 페이지 로드 완료.")

            # 5. 게시판 내용 스크래핑
            print("게시판 내용 스크래핑을 시작합니다...")
            html_content = await page.content()
            
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 정확한 선택자로 게시글 행 목록을 찾습니다.
            board_rows = soup.select('#list_table .tableBody li')
            
            if not board_rows:
                print("게시글 목록을 찾을 수 없습니다.")
                return []

            # 각 게시글 행을 순회
            for row in board_rows:
                # 공지사항 행 건너뛰기 (p.num에 img 태그가 있는 경우)
                if row.select_one('p.num img'):
                    continue

                # 답변이 달렸는지 확인 (span.re_no 태그의 존재 여부로 판단)
                is_answered = row.select_one('p.title span.re_no')
                
                # 답변이 달리지 않은 경우에만 데이터 추출
                if not is_answered:
                    title_elem = row.select_one('p.title a')
                    if title_elem:
                        title = title_elem.text.strip()
                        relative_url = title_elem['href']
                        # URL을 완전한 형태로 만듭니다.
                        content_url = f"http://unam.gen.ms.kr{relative_url}"
                        
                        # 작성자 텍스트 추출 (<span> 태그 제거)
                        name_elem = row.select_one('p.name')
                        if name_elem:
                            # <span> 태그를 찾아 제거합니다.
                            if name_elem.find('span'):
                                name_elem.find('span').decompose()
                            author = name_elem.text.strip()
                        else:
                            author = 'N/A'
                        
                        date_elem = row.select_one('p.date')
                        created_at = date_elem.text.strip() if date_elem else 'N/A'

                        scraped_data.append({
                            'school_name': '운암중학교',
                            'title': title,
                            'content_url': content_url,
                            'author': author,
                            'created_at': created_at,
                            'status': '답변대기'
                        })

        except Exception as e:
            print(f"\n오류가 발생했습니다: {e}")
            await page.screenshot(path="error_page.png")
            print("오류 발생 당시의 화면을 'error_page.png' 파일로 저장했습니다.")

        finally:
            await browser.close()
            print("스크래핑 프로세스를 종료합니다.")
            
    return scraped_data

async def main_async():
    unanswered_posts = await get_unanswered_posts()
    
    if unanswered_posts:
        df = pd.DataFrame(unanswered_posts)
        print("\n[최종 스크래핑 결과]")
        print(df)
        df.to_csv("scraped_board.csv", index=False, encoding="utf-8-sig")
        print("\n'scraped_board.csv' 파일로 저장했습니다.")
    else:
        print("\n새로운 답변대기 게시글이 없습니다.")

if __name__ == "__main__":
    asyncio.run(main_async())
