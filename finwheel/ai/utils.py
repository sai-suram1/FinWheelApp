"""
    Install the Google AI Python SDK

    $ pip install google-generativeai

    See the getting started guide for more information:
    https://ai.google.dev/gemini-api/docs/get-started/python
    """

import os
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai
from dotenv import load_dotenv,dotenv_values
from bank.banking_tools import *
from bank.models import CashAccount
from user.models import *
from ai.models import model_parameters
config = dotenv_values("ai/.env")
from ai.load_creds import *
import decimal
import datetime
#from ai.models import *

genai.configure(api_key=config["api-key"])

    # Create the model
    # See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
    "temperature": 1.8,
    "top_p": 1,
    "top_k": 0,
    "max_output_tokens": 8192,
    #"Content-Type": "application/json",
}


def print_history(hist):
    for x in hist:
        print(f"{x['role']}: {x['parts'][0]}")

def refine_chat_history(history, user):
    # Initialize the chat history list
    hist = []

    # Your chat history with input-output pairs
    chat_history = [
      "input: What should I consider when planning for retirement?",
      "output: When planning for retirement, consider factors such as your target retirement age, expected retirement expenses, sources of retirement income (e.g., Social Security, pensions), and risk tolerance. Diversifying investments, including stocks, bonds, and annuities, can help balance growth potential with risk mitigation.",
      "input: What is the best way to reduce taxes on my investments?",
      "output: Strategies to reduce taxes on investments include utilizing tax-advantaged accounts like 401(k)s and IRAs, holding investments for more than a year to qualify for long-term capital gains tax rates, and harvesting tax losses. Consult a tax advisor for personalized advice.",
      "input: How can I diversify my investment portfolio?",
      "output: To diversify a portfolio, spread investments across various asset classes such as stocks, bonds, real estate, and alternative investments. Diversification helps to reduce risk by not relying on a single asset class. Consider factors like industry, geography, and asset type.",
      "input: What is a safe investment for someone close to retirement?",
      "output: For individuals near retirement, safer investments often include bonds, bond funds, certificates of deposit (CDs), or Treasury Inflation-Protected Securities (TIPS). These options offer lower risk and steady income but may have lower returns.",
      "input: Should I invest in individual stocks or mutual funds?",
      "output: Mutual funds offer diversification and professional management, which reduces risk compared to individual stocks. If you prefer to actively manage your portfolio and are comfortable with risk, individual stocks can offer higher potential returns. Consider your risk tolerance and investment goals.",
      "input: What is the difference between a Roth IRA and a Traditional IRA?",
      "output: A Roth IRA allows tax-free withdrawals in retirement, as contributions are made with after-tax dollars, while a Traditional IRA offers tax-deferred growth, with pre-tax contributions reducing your taxable income now but subjecting withdrawals to taxes in retirement.",
      "input: How do I balance growth and safety in my investments?",
      "output: To balance growth and safety, consider allocating a portion of your portfolio to equities for growth and another portion to fixed income or bonds for safety. Regularly rebalance your portfolio based on market conditions and personal risk tolerance.",
      "input: What are the risks of investing in alternative investments like real estate?",
      "output: Alternative investments, including real estate, can provide diversification but carry risks such as illiquidity, volatility, and the potential for market downturns. It’s essential to assess your risk tolerance and investment horizon before considering alternatives.",
      "input: How do interest rates affect bond prices?",
      "output: Bond prices have an inverse relationship with interest rates. When interest rates rise, bond prices typically fall, and vice versa. This is because higher rates make existing bonds with lower yields less attractive to investors.",
      "input: What type of insurance should I include in my financial plan?",
      "output: Consider life insurance to provide for your dependents, disability insurance to replace income if you're unable to work, and health insurance to cover medical costs. Additionally, long-term care insurance may be necessary as you age.",
      "input: What is the difference between a 401(k) and a 403(b) retirement plan?",
      "output: Both 401(k) and 403(b) plans are tax-advantaged retirement savings accounts, but 403(b) plans are typically offered by non-profit organizations and public schools, while 401(k)s are for private-sector employees. Both allow pre-tax contributions and tax-deferred growth.",
      "input: When should I start withdrawing from my retirement accounts?",
      "output: You must start taking required minimum distributions (RMDs) from most retirement accounts (except Roth IRAs) by April 1 following the year you turn 72. However, you may begin penalty-free withdrawals at age 59½. Withdrawals before that may incur a 10% penalty.",
      "input: How much should I be saving for emergencies?",
      "output: It is generally recommended to keep three to six months’ worth of living expenses in a liquid, easily accessible account like a savings or money market account for emergencies. This helps cover unexpected expenses like medical bills or job loss.",
      "input: What is the role of an investment advisor?",
      "output: An investment advisor provides financial advice or manages portfolios on behalf of clients. They help clients make informed decisions about their investments and financial goals, ensuring their strategies align with risk tolerance and long-term objectives.",
      "input: How does dollar-cost averaging work in investing?",
      "output: Dollar-cost averaging involves consistently investing a fixed amount of money into a particular investment, regardless of its price. This strategy reduces the risk of making large purchases at market peaks by spreading out purchases over time.",
      "input: What are the benefits of investing in index funds?",
      "output: Index funds offer low fees, diversification, and consistent returns by tracking the performance of a market index, such as the S&P 500. They are considered a passive investment strategy and often outperform actively managed funds over the long term.",
      "input: How can I manage investment risk?",
      "output: You can manage risk by diversifying your portfolio, setting appropriate asset allocations based on your risk tolerance, and regularly reviewing and adjusting your investments as market conditions or personal goals change.",
      "input: What is the difference between a growth stock and a value stock?",
      "output: Growth stocks are shares in companies expected to grow at an above-average rate compared to other firms, often reinvesting earnings rather than paying dividends. Value stocks are undervalued by the market but have strong fundamentals and may offer dividends.",
      "input: How can I plan for long-term care expenses?",
      "output: Long-term care insurance can help cover the cost of services such as nursing home care or in-home assistance. Consider purchasing coverage in your 50s or early 60s to secure affordable premiums before age-related conditions arise.",
      "input: What is the best way to save for a child's college education?",
      "output: A 529 savings plan offers tax advantages and can be used to pay for qualified education expenses like tuition, books, and room and board. Some states also provide tax deductions or credits for contributions to these plans.",
      "input: Should I invest in bonds during a recession?",
      "output: Bonds can be a safer investment during a recession due to their relatively stable returns compared to stocks. Government bonds or investment-grade corporate bonds may provide a steady income stream and preserve capital during economic downturns.",
      "input: How does compound interest benefit my investments?",
      "output: Compound interest helps your investment grow faster because it is calculated on the initial principal and the accumulated interest from previous periods. The longer your investment compounds, the more exponential growth it generates.",
      "input: What is the difference between a Roth 401(k) and a traditional 401(k)?",
      "output: A Roth 401(k) allows you to contribute after-tax dollars, and qualified withdrawals in retirement are tax-free. A traditional 401(k) uses pre-tax dollars, providing an immediate tax break, but withdrawals in retirement are taxed as ordinary income.",
      "input: What are the tax implications of withdrawing early from a retirement account?",
      "output: Withdrawing from a traditional IRA or 401(k) before age 59½ generally incurs a 10% penalty plus ordinary income tax. However, exceptions include withdrawals for first-time home purchases, medical expenses, or certain hardships.",
      "input: How do mutual funds work?",
      "output: Mutual funds pool money from many investors to purchase a diversified portfolio of stocks, bonds, or other securities. Investors share in the gains or losses of the fund based on the proportion of their investment. Mutual funds are managed by professionals.",
      "input: What is asset allocation, and why is it important?",
      "output: Asset allocation is the process of dividing investments among different asset categories, such as stocks, bonds, and cash. It is important because it helps balance risk and return by diversifying investments across assets that perform differently under various market conditions.",
      "input: How can I protect my investments from inflation?",
      "output: To protect against inflation, consider investing in assets that typically rise in value over time, such as stocks, real estate, or Treasury Inflation-Protected Securities (TIPS). Maintaining a diversified portfolio can also help offset inflation risks.",
      "input: What is a target-date fund?",
      "output: A target-date fund automatically adjusts the allocation of stocks, bonds, and other assets based on your expected retirement date. As the target date approaches, the fund gradually shifts toward more conservative investments to reduce risk.",
      "input: How does a bond ladder strategy work?",
      "output: A bond ladder involves buying bonds with different maturities to reduce interest rate risk. As each bond matures, the principal can be reinvested into new bonds. This strategy provides a steady stream of income and can take advantage of changing interest rates.",
      "input: What factors should I consider before buying a home?",
      "output: Before buying a home, consider your budget, the total costs of ownership (including maintenance, property taxes, and insurance), your credit score, and the long-term financial commitment of a mortgage. Evaluate whether you plan to stay in the home long-term.",
      "input: Should I pay off my mortgage early or invest the extra money?",
      "output: Deciding whether to pay off your mortgage early or invest depends on your interest rate, investment return potential, and risk tolerance. Paying off a mortgage offers guaranteed savings, while investing may yield higher returns but comes with risk.",
      "input: What is the role of a financial advisor?",
      "output: A financial advisor helps clients create and manage financial plans, providing advice on budgeting, investments, retirement, tax strategies, and estate planning. They ensure that financial goals align with a client's risk tolerance and life stage.",
      "input: What is rebalancing, and why is it necessary?",
      "output: Rebalancing involves adjusting your portfolio to its target asset allocation after market fluctuations. It helps maintain the desired level of risk by selling overperforming assets and buying underperforming ones, ensuring the portfolio remains aligned with your goals.",
      "input: How can I protect my family financially after my death?",
      "output: Life insurance can provide a lump sum to your beneficiaries to cover living expenses, debts, and future financial needs. A will, along with other estate planning tools like trusts, can ensure that your assets are distributed according to your wishes.",
      "input: What is a capital gain, and how is it taxed?",
      "output: A capital gain is the profit from selling an asset like stocks or real estate for more than its purchase price. Long-term capital gains (assets held for over a year) are taxed at a lower rate than short-term gains, which are taxed as ordinary income.",
      "input: How do exchange-traded funds (ETFs) differ from mutual funds?",
      "output: ETFs are traded on stock exchanges like individual stocks and typically have lower expense ratios than mutual funds. While mutual funds are actively managed, many ETFs passively track an index. ETFs offer flexibility and tax efficiency but may involve trading costs.",
      "input: How should I plan for healthcare costs in retirement?",
      "output: Planning for healthcare costs in retirement includes budgeting for premiums, out-of-pocket expenses, and long-term care. Consider using a Health Savings Account (HSA) if available, which offers tax advantages for medical expenses.",
      "input: What is the difference between short-term and long-term investments?",
      "output: Short-term investments typically have a horizon of one to three years and include assets like savings accounts or bonds. Long-term investments are held for many years, aiming for higher returns through stocks, real estate, or retirement accounts.",
      "input: What is the impact of inflation on savings?",
      "output: Inflation reduces the purchasing power of savings, meaning that over time, the same amount of money buys fewer goods and services. To counter inflation, consider investing in assets that typically grow in value, like stocks, bonds, or real estate.",
      "input: How can I start investing with a small amount of money?",
      "output: You can start investing with a small amount by using low-cost investment options like index funds or ETFs. Many brokerages offer fractional shares, allowing you to buy portions of stocks or funds without needing to purchase a full share.",
      "input: How can I minimize fees on my investments?",
      "output: To minimize fees, consider investing in low-cost index funds or ETFs with low expense ratios. Avoid frequent trading, which can incur transaction fees, and review advisory fees or account management costs to ensure they align with your financial goals.",
      "input: What is the role of a 529 plan in education savings?",
      "output: A 529 plan is a tax-advantaged savings account designed to encourage saving for future education costs. Contributions grow tax-free, and withdrawals for qualified education expenses, like tuition and books, are not subject to federal taxes.",
      "input: What are the benefits of automatic investment plans?",
      "output: Automatic investment plans help build wealth over time by setting up regular, automatic contributions to investment accounts. This consistent investing approach helps you stay disciplined and avoid trying to time the market.",
      "input: What is the difference between a fixed-rate and adjustable-rate mortgage?",
      "output: A fixed-rate mortgage maintains the same interest rate throughout the loan term, while an adjustable-rate mortgage (ARM) has an interest rate that may fluctuate after an initial fixed period. ARMs may offer lower initial rates but carry the risk of future increases.",
      "input: How can I manage debt effectively?",
      "output: Managing debt involves prioritizing high-interest debt, such as credit cards, for quicker repayment. Consider consolidating debt for lower interest rates, setting up automatic payments, and avoiding taking on new debt unless necessary.",
      "input: What is the advantage of a Health Savings Account (HSA)?",
      "output: A Health Savings Account (HSA) offers triple tax benefits: contributions are tax-deductible, earnings grow tax-free, and withdrawals for qualified medical expenses are also tax-free. HSAs can also be used for retirement savings if not needed for healthcare.",
      "input: What is the difference between a SEP IRA and a SIMPLE IRA?",
      "output: A SEP IRA is a retirement plan typically used by self-employed individuals or small business owners, allowing employers to make contributions. A SIMPLE IRA is a retirement plan for small businesses with fewer than 100 employees, where both employers and employees can contribute.",
      "input: What are some strategies to pay off student loans faster?",
      "output: Strategies to pay off student loans faster include making extra payments when possible, refinancing for a lower interest rate, or switching to a biweekly payment schedule. Focus on higher-interest loans first to save on overall interest costs.",
      "input: How can I improve my credit score?",
      "output: To improve your credit score, pay bills on time, keep credit card balances low relative to your credit limit, avoid opening too many new accounts, and review your credit report regularly for errors. A strong credit score can help secure better loan terms.",
      "input: What is a dividend reinvestment plan (DRIP)?",
      "output: A dividend reinvestment plan (DRIP) allows shareholders to reinvest their cash dividends into additional shares of the company’s stock, often without paying brokerage fees. This can accelerate wealth accumulation through compound growth.",
      "input: What is a backdoor Roth IRA, and how does it work?",
      "output: A backdoor Roth IRA is a strategy where individuals who exceed the income limits for a Roth IRA contribute to a traditional IRA and then convert those funds to a Roth IRA. This allows higher-income earners to take advantage of tax-free withdrawals in retirement.",
      "input: What are some ways to avoid probate?",
      "output: Ways to avoid probate include naming beneficiaries on retirement accounts, using joint ownership for property, establishing a revocable living trust, and designating payable-on-death (POD) or transfer-on-death (TOD) accounts.",
      "input: How can I make charitable donations more tax-efficient?",
      "output: To make charitable donations more tax-efficient, consider donating appreciated securities, setting up a donor-advised fund, or making Qualified Charitable Distributions (QCDs) from an IRA if you are over age 70½. These strategies can reduce capital gains taxes and taxable income.",
      "input: What is the wash-sale rule in stock trading?",
      "output: The wash-sale rule prohibits claiming a tax deduction for a loss on the sale of a security if you purchase the same or a substantially identical security within 30 days before or after the sale. This prevents investors from selling and immediately repurchasing for tax benefits.",
      "input: What is the difference between active and passive investing?",
      "output: Active investing involves making specific investments in an effort to outperform a market index, usually requiring frequent trading and research. Passive investing, like buying index funds, involves following a market index with minimal buying and selling. Passive investing generally has lower fees.",
      "input: How should I invest if I’m nearing retirement?",
      "output: If you are nearing retirement, it’s important to reduce risk by shifting investments toward more conservative assets, such as bonds, stable value funds, or dividend-paying stocks. Ensure your portfolio is diversified and consider allocating funds for guaranteed income, such as an annuity.",
      "input: What is the role of an estate plan?",
      "output: An estate plan outlines how your assets will be managed and distributed after your death. It includes a will, power of attorney, healthcare directives, and trusts. A well-constructed estate plan can minimize taxes and probate fees, ensuring your wishes are carried out.",
      "input: What are the advantages of an annuity in retirement planning?",
      "output: Annuities provide guaranteed income in retirement, which can help cover essential living expenses. Fixed annuities offer a stable income stream, while variable annuities offer growth potential based on investment performance. Annuities can also help manage longevity risk.",
      "input: What is a custodial account, and when should I use one?",
      "output: A custodial account is a financial account set up for the benefit of a minor, managed by an adult until the child reaches legal age. It can be used for college savings or general financial needs. Once the child reaches adulthood, they gain full control of the account.",
      "input: How do I rollover my 401(k) into an IRA?",
      "output: To roll over your 401(k) into an IRA, request a direct rollover from your 401(k) plan administrator to your new IRA provider. This avoids taxes and penalties. If the funds are distributed directly to you, they must be deposited into an IRA within 60 days to avoid penalties.",
      "input: What are the risks of investing in cryptocurrency?",
      "output: Cryptocurrencies are highly volatile and subject to significant price swings. They are not backed by any government or central authority, making them speculative. There is also the risk of losing assets due to hacking, fraud, or lack of regulation in this emerging market.",
      "input: What is dollar-cost averaging, and why should I use it?",
      "output: Dollar-cost averaging is a strategy where you invest a fixed amount of money at regular intervals, regardless of the asset's price. This reduces the risk of investing a large sum during a market peak and takes advantage of market fluctuations by buying more shares when prices are low.",
      "input: How do I choose the right life insurance policy?",
      "output: When choosing life insurance, consider factors such as your financial obligations, the amount of income replacement needed, and whether a term or whole life policy is best suited for your needs. Term life insurance offers affordable, temporary coverage, while whole life provides permanent coverage with a savings component.",
      "input: What is the 60-day rollover rule?",
      "output: The 60-day rollover rule applies to retirement account distributions. If you take a distribution from an IRA or 401(k), you have 60 days to redeposit the funds into the same or another eligible retirement account to avoid taxes and penalties.",
      "input: What are capital gains distributions in a mutual fund?",
      "output: Capital gains distributions occur when a mutual fund sells securities at a profit and distributes those gains to shareholders. These distributions are typically taxable, even if the investor reinvests them in the fund. Consider tax-efficient funds to minimize these distributions.",
      "input: What is margin trading, and how does it work?",
      "output: Margin trading allows you to borrow money from a broker to buy securities, using your investments as collateral. While it can amplify gains, it also increases risk, as losses are magnified. If the value of your securities falls, you may be required to deposit additional funds to meet margin calls.",
      "input: How should I invest a windfall or inheritance?",
      "output: When receiving a windfall or inheritance, first pay off high-interest debt, establish an emergency fund, and invest in tax-efficient vehicles like retirement accounts. Work with a financial advisor to create a long-term plan that aligns with your goals and risk tolerance.",
      "input: What is a required minimum distribution (RMD)?",
      "output: Required minimum distributions (RMDs) are mandatory withdrawals from retirement accounts, such as traditional IRAs and 401(k)s, starting at age 72. Failure to take an RMD results in a significant tax penalty of 50% of the amount not withdrawn.",
      "input: What are qualified dividends, and how are they taxed?",
      "output: Qualified dividends are dividends paid by U.S. corporations or qualified foreign companies that meet certain IRS criteria. They are taxed at the lower long-term capital gains tax rate, which is more favorable than ordinary income tax rates.",
      "input: What are the tax benefits of investing in municipal bonds?",
      "output: Municipal bonds are generally exempt from federal income taxes, and if issued by your state or locality, may also be exempt from state and local taxes. This makes them an attractive option for investors in higher tax brackets looking to minimize taxable income.",
      "input: How does a reverse mortgage work?",
      "output: A reverse mortgage allows homeowners aged 62 or older to convert part of their home equity into cash. The loan is repaid when the homeowner sells the home, moves, or passes away. However, reverse mortgages can reduce the inheritance for heirs and carry fees.",
      "input: How can I ensure my spouse is financially secure if I pass away?",
      "output: To ensure your spouse’s financial security, establish life insurance policies, update beneficiaries on retirement accounts, and create an estate plan. A joint bank account or trust can ensure your spouse has immediate access to funds without probate delays.",
      "input: What are the differences between tax-deferred and tax-exempt accounts?",
      "output: Tax-deferred accounts (like 401(k)s and traditional IRAs) allow contributions to grow without being taxed until withdrawals, while tax-exempt accounts (like Roth IRAs) allow for tax-free withdrawals in retirement after contributions have been taxed. Choose based on your expected future tax rates.",
      "input: What is the difference between a limit order and a market order?",
      "output: A market order executes immediately at the current market price, while a limit order only executes when the asset reaches a specified price. Limit orders help control the price you pay but may not be executed if the price doesn’t reach your target.",
      "input: What are the advantages of joint accounts for married couples?",
      "output: Joint accounts offer shared access to funds and simplify bill payments and budgeting for married couples. They also provide easy access to funds in case of death or incapacitation. However, joint accounts can complicate financial separation in case of divorce.",
      "input: How do I plan for estate taxes?",
      "output: Estate planning strategies to minimize estate taxes include setting up trusts, gifting assets while living, and using the federal estate tax exemption. An estate tax applies if your estate exceeds the exemption limit ($12.92 million per person in 2023). Consult an estate planning attorney for personalized advice.",
      "input: What is an IRA rollover, and when should I use one?",
      "output: An IRA rollover allows you to move funds from one retirement account, such as a 401(k), into an IRA without paying taxes or penalties. It’s often used when changing jobs or consolidating retirement accounts for simplified management and better investment options.",
      "input: What should I consider before refinancing my mortgage?",
      "output: Before refinancing your mortgage, consider the new interest rate, loan term, closing costs, and how long you plan to stay in the home. Refinancing can lower monthly payments or reduce interest over the life of the loan but may extend the repayment period.",
      "input: What is a fiduciary, and why is it important to work with one?",
      "output: A fiduciary is legally obligated to act in your best financial interest, providing advice that is free from conflicts of interest. Working with a fiduciary ensures that your financial advisor or planner prioritizes your goals and needs above their own compensation.",
      "input: How can I reduce the risk of identity theft?",
      "output: To reduce the risk of identity theft, use strong passwords, enable two-factor authentication, monitor your credit report regularly, and avoid sharing personal information online. Consider freezing your credit if you suspect your identity has been compromised.",
      "input: What are the benefits of using a trust in estate planning?",
      "output: A trust allows assets to be managed by a trustee for the benefit of beneficiaries, offering control over distributions and avoiding probate. Trusts can provide tax advantages, protect assets from creditors, and ensure privacy in estate settlements.",
      "input: How can I avoid penalties when withdrawing from an IRA before age 59½?",
      "output: You can avoid penalties on early IRA withdrawals under certain circumstances, such as for first-time home purchases, higher education expenses, or substantial medical bills. Additionally, using a 72(t) distribution method allows penalty-free early withdrawals based on a series of substantially equal payments.",
      "input: What is the best way to save for retirement as a freelancer?",
      "output: Freelancers can save for retirement using options like a SEP IRA, SIMPLE IRA, or solo 401(k). These accounts allow higher contribution limits than traditional IRAs, offering more flexibility to save for retirement. Contributing to these accounts is tax-deductible, helping reduce current tax liabilities.",
      "input: How does inflation affect my investments?",
      "output: Inflation erodes purchasing power, which can reduce the real value of fixed-income investments. To counter inflation, consider including stocks, real estate, or inflation-protected securities (like TIPS) in your portfolio. These assets tend to rise in value over time, helping offset inflation risks.",
      "input: What is the benefit of consolidating retirement accounts?",
      "output: Consolidating retirement accounts into a single IRA or 401(k) simplifies management, reduces fees, and allows for more effective portfolio allocation. It also reduces the number of required minimum distributions (RMDs) when you reach retirement age, making it easier to manage withdrawals.",
      "input: How can I optimize Social Security benefits?",
      "output: To maximize Social Security benefits, delay claiming until age 70 to receive the maximum benefit. If possible, coordinate spousal benefits and take advantage of strategies like restricted application or delaying spousal benefits to boost overall retirement income.",
      "input: What are the tax implications of gifting money to family members?",
      "output: You can give up to $17,000 per year (as of 2023) to an individual without triggering the federal gift tax. For larger gifts, the lifetime exclusion applies (currently $12.92 million), allowing tax-free transfers up to that limit. Any amount above the exclusion is subject to gift tax.",
      "input: What are the advantages of automatic 401(k) contributions?",
      "output: Automatic contributions to a 401(k) help you consistently save for retirement, taking advantage of employer matching contributions and tax deferrals. It ensures disciplined saving without needing to remember or manually transfer funds, making it easier to reach your retirement goals.",
      "input: Should I buy long-term care insurance?",
      "output: Long-term care insurance can help cover the cost of extended care services, such as nursing home care, assisted living, or in-home care. Purchasing a policy earlier in life, typically in your 50s, can secure lower premiums. This insurance helps protect your retirement savings from being depleted by healthcare costs.",
      "input: What is tax-loss harvesting, and how can it help me?",
      "output: Tax-loss harvesting involves selling investments at a loss to offset gains in other investments, thus reducing your taxable income. It’s an effective strategy to lower your overall tax liability while allowing you to reinvest in assets for future growth. Be mindful of the wash-sale rule when using this strategy.",
      "input: What are the advantages of a spousal IRA?",
      "output: A spousal IRA allows a non-working spouse to contribute to an IRA based on the working spouse’s income. This helps both spouses save for retirement, even if one does not have earned income. Both traditional and Roth IRAs are options, depending on your tax strategy.",
      "input: How can I protect my assets from lawsuits or creditors?",
      "output: To protect assets, consider strategies such as setting up an irrevocable trust, using retirement accounts like IRAs or 401(k)s (which often have creditor protection), purchasing liability insurance, or incorporating your business. Each method provides varying degrees of asset protection.",
      "input: What is a financial power of attorney, and why do I need one?",
      "output: A financial power of attorney allows a designated person to manage your finances if you become incapacitated. It’s a crucial part of an estate plan, ensuring bills are paid, assets are managed, and financial decisions are made according to your wishes if you are unable to do so.",
      "input: What are the benefits of a Roth conversion?",
      "output: A Roth conversion allows you to move funds from a traditional IRA or 401(k) to a Roth IRA, where future withdrawals are tax-free. While you’ll pay taxes on the conversion amount, this strategy can be beneficial if you expect to be in a higher tax bracket in retirement.",
      "input: What is a money market fund, and how does it work?",
      "output: A money market fund is a type of mutual fund that invests in short-term, high-quality debt securities like Treasury bills and commercial paper. It offers liquidity and safety but typically lower returns compared to other investments. Money market funds are often used for emergency savings or as a cash equivalent in a portfolio.",
      "input: How can I use a 1031 exchange to defer capital gains taxes?",
      "output: A 1031 exchange allows you to defer paying capital gains taxes when selling an investment property by reinvesting the proceeds into a similar property. This strategy can help real estate investors grow their portfolios while postponing tax liabilities. To qualify, the new property must be identified within 45 days and closed within 180 days of the sale.",
      "input: What is a charitable remainder trust (CRT)?",
      "output: A charitable remainder trust (CRT) is an irrevocable trust that provides income to the trust’s beneficiaries for a set period, after which the remainder is donated to a charity. It offers tax benefits, including an income tax deduction, and helps donors support causes while still receiving income.",
      "input: How can I reduce estate taxes?",
      "output: Strategies to reduce estate taxes include gifting assets during your lifetime, setting up irrevocable trusts, purchasing life insurance to cover estate tax liabilities, and taking advantage of the federal estate tax exemption. Consult an estate planning attorney for personalized strategies.",
      "input: How does an irrevocable life insurance trust (ILIT) work?",
      "output: An irrevocable life insurance trust (ILIT) removes the life insurance policy from your taxable estate, allowing the proceeds to pass to your beneficiaries free of estate taxes. The trust owns the policy, and upon your death, the ILIT provides liquidity to pay estate taxes or support beneficiaries.",
      "input: What is the difference between a revocable and irrevocable trust?",
      "output: A revocable trust can be altered or dissolved by the grantor during their lifetime, providing flexibility. An irrevocable trust cannot be changed once it is established, but it offers greater protection from creditors and may help reduce estate taxes by removing assets from the grantor’s estate.",
      "input: How does an indexed universal life (IUL) policy work?",
      "output: An indexed universal life (IUL) policy is a type of permanent life insurance that offers a death benefit and cash value growth linked to the performance of an equity index, like the S&P 500. It provides downside protection with a guaranteed minimum return while allowing for potential upside growth.",
      "input: What are the advantages of an umbrella insurance policy?",
      "output: An umbrella insurance policy provides additional liability coverage beyond the limits of your homeowners, auto, or other personal insurance policies. It helps protect your assets from large claims or lawsuits, offering an extra layer of security for relatively low premiums.",
      "input: What are the tax benefits of contributing to a Health Savings Account (HSA)?",
      "output: Contributions to an HSA are tax-deductible, earnings grow tax-free, and withdrawals for qualified medical expenses are also tax-free. After age 65, you can use HSA funds for non-medical expenses, though they will be taxed as ordinary income. HSAs are a powerful tool for managing healthcare costs in retirement.",
      "input: What is a stretch IRA, and how does it work?",
      "output: A stretch IRA allows non-spouse beneficiaries of an IRA to “stretch” distributions over their lifetime, deferring taxes on withdrawals and allowing the inherited IRA to continue growing tax-deferred. This strategy can significantly extend the tax advantages of the original IRA. Recent changes to tax laws now require most non-spouse beneficiaries to withdraw the entire balance within 10 years, but a stretch IRA is still an option for certain beneficiaries.",
      "input: How can I plan for early retirement?",
      "output: To plan for early retirement, maximize contributions to retirement accounts, build a robust taxable investment portfolio, and minimize debt. Consider healthcare costs before Medicare eligibility and ensure you have enough assets to support a potentially longer retirement. Additionally, factor in penalties for early withdrawals from retirement accounts, and plan for alternative income sources.",
      "input: What is the difference between secured and unsecured debt?",
      "output: Secured debt is backed by collateral, such as a mortgage or auto loan, meaning the lender can seize the asset if the borrower defaults. Unsecured debt, such as credit card debt or personal loans, is not backed by collateral, so lenders take on more risk, often resulting in higher interest rates.",
      "input: How can I protect my portfolio during a market downturn?",
      "output: To protect your portfolio during a market downturn, consider diversifying across asset classes, maintaining a balanced mix of stocks and bonds, and holding cash or cash equivalents. Avoid panic selling and stay focused on long-term investment goals. Rebalancing can also help manage risk.",
      "input: What is the benefit of owning dividend-paying stocks?",
      "output: Dividend-paying stocks provide regular income, which can help offset market volatility. Companies that pay dividends are often financially stable, making these stocks a more conservative investment. Dividends can be reinvested to compound returns over time.",
      "input: How does a variable annuity work?",
      "output: A variable annuity allows investors to allocate their contributions to various subaccounts, similar to mutual funds. The value of the annuity fluctuates based on the performance of the chosen investments. Variable annuities offer tax-deferred growth and the option for a guaranteed death benefit or lifetime income. However, they often come with higher fees than other investment products.",
      "input: What is the difference between a fixed annuity and a variable annuity?",
      "output: A fixed annuity provides guaranteed payments at a fixed interest rate, making it a conservative option for retirees seeking stable income. A variable annuity offers the potential for higher returns based on the performance of underlying investments but comes with greater risk. Both can provide lifetime income options.",
      "input: What is the difference between preferred stock and common stock?",
      "output: Preferred stockholders have priority over common stockholders in receiving dividends and assets in the event of liquidation. Preferred stock typically pays a fixed dividend and does not have voting rights. Common stockholders may have voting rights and benefit from capital appreciation but are last to receive dividends and assets.",
      "input: How can I estimate my Social Security benefits?",
      "output: You can estimate your Social Security benefits by creating a “my Social Security” account on the Social Security Administration’s website. The estimate is based on your earnings history and when you plan to start receiving benefits. Benefits increase the longer you delay taking them, up to age 70.",
      "input: What is probate, and how can I avoid it?",
      "output: Probate is the legal process of settling an estate after someone’s death. It can be time-consuming and costly. To avoid probate, you can use tools like living trusts, joint ownership, payable-on-death accounts, and naming beneficiaries on retirement accounts and life insurance policies.",
      "input: What are the benefits of contributing to a Roth IRA versus a traditional IRA?",
      "output: A Roth IRA allows for tax-free withdrawals in retirement, as contributions are made with after-tax dollars. A traditional IRA offers tax-deferred growth and may provide an immediate tax deduction for contributions. The best option depends on your current tax situation and expected future tax rate.",
      "input: How does a fixed-index annuity work?",
      "output: A fixed-index annuity offers a guaranteed minimum return and allows participation in the growth of a stock market index, such as the S&P 500. While the annuity provides upside potential, there are often caps or limits on gains. Fixed-index annuities are suitable for those seeking a balance between growth and protection.",
      "input: What are the advantages of contributing to a 401(k) plan?",
      "output: Contributing to a 401(k) plan allows you to save for retirement on a tax-deferred basis, reducing your current taxable income. Many employers offer matching contributions, effectively giving you free money for your retirement. Contributions grow tax-deferred until withdrawn in retirement, at which point they are taxed as ordinary income.",
      "input: How do I calculate my net worth?",
      "output: Your net worth is the difference between your total assets (such as cash, investments, and property) and your total liabilities (such as mortgages, loans, and credit card debt). A positive net worth indicates financial health, while a negative net worth may suggest that you owe more than you own.",
      "input: What are the risks of using leverage in investing?",
      "output: Using leverage in investing amplifies both potential gains and losses. While borrowing money to invest can enhance returns in a rising market, it also increases exposure to downside risk. If the value of your investment decreases, you may face margin calls or be forced to sell assets to repay the loan.",
      "input: What is the difference between a credit score and a credit report?",
      "output: A credit report is a detailed record of your credit history, including loan accounts, credit inquiries, and payment history. Your credit score is a numerical representation of your creditworthiness, calculated based on the information in your credit report. Lenders use both to evaluate your credit risk.",
      "input: What is a revocable living trust, and how does it work?",
      "output: A revocable living trust allows you to manage and distribute your assets during your lifetime and after your death without going through probate. The trust can be altered or revoked at any time, giving you flexibility. It also provides privacy, as trust assets are not part of the public probate process.",
    ]

    # Loop through chat_history and convert each input-output pair
    for i in range(0, len(chat_history), 2):
        user_input = chat_history[i].replace("input: ", "").strip()
        model_response = chat_history[i + 1].replace("output: ", "").strip()
        
        hist.append({
            "role": "user",
            "parts": [user_input],
        })
        hist.append({
            "role": "model",
            "parts": [model_response],
        })

    # Add conversation history from the database
    lk = model_parameters.objects.all()
    for d in lk:
        hist.append({
            "role": "user",
            "parts": [d.user_msg],
        })
        hist.append({
            "role": "model",
            "parts": [d.model_msg],
        })

    for x in history.order_by('order'):
        hist.append({
            "role": "user",
            "parts": [x.user_message],
        })
        hist.append({
            "role": "model",
            "parts": [x.chatbot_response],
        })

    # Add financial details and asset information
    cash = dict(get_account_info(acct=CashAccount.objects.get(for_user=user)))["cash"]
    hist.append({
        "role": "user",
        "parts": [
            f"THE USER'S ACCOUNT HAS ${float(cash)} in cash",
        ],
    })
    hist.append({
        "role": "model",
        "parts": [
            "I understand that the user only has this much in cash and I will ensure that his balance stays above $0.01 with any transaction he does."
        ],
    })

    assets = get_positions_from_account(user=CashAccount.objects.get(for_user=user))
    for p in assets:
        hist.append({
            "role": "user",
            "parts": [
                f"Please process this. This is one of the user's assets: {p}. \n Find the proper name of the company of which the asset is held. USE BOTH THE TICKER AND THE EXCHANGE NAME TO HELP YOU.",
            ],
        })
        hist.append({
            "role": "model",
            "parts": [
                "I understand that the user has that asset in his portfolio. I WILL USE BOTH THE TICKER AND THE EXCHANGE NAME TO FIND THE COMPANY NAME."
            ],
        })

    # Print the chat history for debugging purposes
    print(print_history(hist))
    return hist



#print('Available base models:', [m.name for m in genai.list_models()])
model = genai.GenerativeModel(model_name="gemini-1.5-pro", generation_config=generation_config)


def find_and_make_trade(user, history):
    ana = model.start_chat(history = refine_chat_history(history, user))
    x = ana.send_message("""What is the trade that needs to be made after looking at the history of the conversation?
        I want the following returned in this exact order:
        

        TICKER: <TICKER>
        ORDER SIDE: <buy, sell>
        TIME IN FORCE: <day, gtc, otp>
        TYPE: <market, limit, stop_limit, trailing_stop>
        (gtc means "Good until Canceled" and otp means "Official Opening Price")
        QUANTITY OF SHARES: <qty>
        OR 
        AMOUNT TO INVEST: <cash_amt>
        """)
    #print(x.text)
    """
        DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 
        WHEN I ASK FOR THE TRADE THAT IS NEEDED TO BE MADE
        I want the following returned in this exact order:
        

        TICKER: <TICKER>
        ORDER SIDE: <BUY, SELL>
        TIME IN FORCE: <day, gtc, otp>
        (gtc means "Good until Canceled" and otp means "Official Opening Price")
        QUANTITY OF SHARES: <qty>
        OR 
        AMOUNT TO INVEST: <cash_amt>
    """
    
    print(x.text)
    lk = x.text.split("\n")
    #print("List: "+str(lk))
    info = []
    for p in lk:
        if p == '':
            continue
        else:
            s = p.split(":")
            print(s)
            info.append({s[0].strip():s[1].strip()})
    #print("Dict: "+str(info))
    print("processing order")
    xy = None
    if "QUANTITY OF SHARES" in x.text and "PRICEPOINT" in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], qty=info[4]["QUANTITY OF SHARES"], cash_account=CashAccount.objects.get(for_user=user), pricept=info[5]["PRICEPOINT"])
    elif "AMOUNT TO INVEST" in x.text and "PRICEPOINT" in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], cash_amt=info[4]["AMOUNT TO INVEST"], cash_account=CashAccount.objects.get(for_user=user),pricept=info[5]["PRICEPOINT"])
    elif "QUANTITY OF SHARES" in x.text and "PRICEPOINT" not in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], qty=info[4]["QUANTITY OF SHARES"], cash_account=CashAccount.objects.get(for_user=user),cash_amt = None, pricept=None)
    elif "AMOUNT TO INVEST" in x.text and "PRICEPOINT" not in x.text:
        xy = process_order(ticker=info[0]["TICKER"], side=info[1]["ORDER SIDE"], type=info[3]["TYPE"], time=info[2]["TIME IN FORCE"], cash_amt=info[4]["AMOUNT TO INVEST"], cash_account=CashAccount.objects.get(for_user=user), qty=None, pricept=None)

    return f"Order had been made. Order ID is: {str(xy)}"

def create_financial_plan(user, history):
    analyzer = model.start_chat(history = refine_chat_history(history, user))
    xt = analyzer.send_message("What should be done for the financial plan")
    """
    PLAN TO TRAIN
    
    ADMIN PRIVELIGES: 
    - When I ask for analyzing what should be done for this financial plan, I want the following to the returned in this exact order. 
    DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 

    INVESTMENT FREQUENCY: (Choose from DAY, WEEK, MONTH)
    INVESTMENT AMOUNT: <Investment amount, NO $>

    When I ask for all the assets to be invested in with the new portfolio, each asset must be listed in this exact order. 
    DO NOT USE ANY MARKDOWN OR OTHER TEXTUAL ADJUSTMENTS. 

    ASSET TICKER: <asset ticker>
    INVESTMENT FREQUENCY: (Choose from DAY, WEEK, MONTH)
    INVESTMENT AMOUNT: <Investment amount, NO $>
    ~
    """

    #print(xt.text)
    lk = xt.text.split("\n")
    investment_freq = lk[0].split(":")[1].strip()
    investment_amt = float(lk[1].split(":")[1].strip())
    #print(investment_freq)
    #print(investment_amt)
    assets = []
    xt = analyzer.send_message("What are all of the assets the user wants to invest in?")
    print(xt.text)
    kj = xt.text.split("~")
    for p in kj:
        stuff = p.split("\n")
        #print(stuff)
        asd = {}
        for d in stuff:
            if d == '' or d == ' ':
                continue
            else:
                #print(d.split(":"))
                asd.update({d.split(":")[0]: d.split(":")[1].strip()})
        assets.append(asd)
    print(assets)

    #make financial plan
    try:
        f = FinancialPlan.objects.get(for_user=user)
    except Exception:
        FinancialPlan.objects.filter(for_user=user).delete()
        f = FinancialPlan(for_user=user, recurring_deposit_amount=decimal.Decimal(investment_amt), recurring_deposit_frequency=investment_freq, last_recurring_deposit=datetime.datetime.now(), next_recurring_deposit = datetime.datetime.now()+datetime.timedelta(hours=(24*30)))
        f.save()

    for lk in assets:
        if "ASSET TICKER" in lk.keys() and "INVESTMENT FREQUENCY" in lk.keys() and ("INVESTMENT AMOUNT" in lk.keys() or "INVESTMENT AMOUNT" in lk.keys() or "INVESTMENT AMOUNT" in lk.keys()):
            try:
                stockPlan = StockFinancialPlan.objects.get(for_user=user, ticker=lk["ASSET TICKER"])
                stockPlan.recurring_deposit_frequency = lk["INVESTMENT FREQUENCY"]
                stockPlan.recurring_deposit_amount = decimal.Decimal(lk["INVESTMENT AMOUNT"])
            except StockFinancialPlan.DoesNotExist:
                stockPlan = StockFinancialPlan(for_user=user, ticker=lk["ASSET TICKER"], reccuring_deposit_amount = decimal.Decimal(lk["INVESTMENT AMOUNT"]), recurring_deposit_frequency=lk["INVESTMENT FREQUENCY"], last_recurring_deposit=datetime.datetime.now(), next_recurring_desposit=datetime.datetime.now()+datetime.timedelta(hours=(24*30)))
                stockPlan.save()
        else:
            continue
        
    
    return True

def get_asset_data(history, user):
    analyzer = model.start_chat(history = refine_chat_history(history, user))
    
    texts = []
    xt = ""
    while len(texts) != 2:
        xt = analyzer.send_message(""" look at the history of the conversation and return one of the following: 

        DO NOT ADD ANY TEXTUAL CHANGES. 

        EARNINGS
        INCOME_STATEMENT
        BALANCE_SHEET
        CASH_FLOW
        CURRENT_PRICE
        QUOTE

        After returning that first line, return the Stock Ticker of the stock to be analyzed. 
        DO NOT ADD ANY TEXTUAL CHANGES.""")
        print(xt.text)
        if "I understand" in xt.text:
            continue
        texts = xt.text.split("\n")
        for v in texts:
            if v == '' or v == "":
                texts.remove(v)
        print(texts)
        if len(texts) != 2:
            continue
    print(texts)
    """
    # replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
    url = f'https://www.alphavantage.co/query?function={str(texts[0]).strip()}&symbol={str(texts[1]).strip()}&apikey={config["alpha-vantage-api"]}'
    print(url)
    r = requests.get(url)
    print(r.status_code)
    data = r.json()

    print(data)
    for x in range(5):
        try:
            final_table = analyzer.send_message(f"Within the data given, find the report the user is looking for and return that specific data. Turn that said data into a HTML table. ONLY RETURN THE HTML TABLE FOR THIS: \n {data}")
            break
        except Exception:
            continue
    """
    import yfinance as yf

    stock = yf.Ticker(str(texts[1]).strip())
    final_info = ""

    if str(texts[0]).strip() == "BALANCE_SHEET":
        final_info = stock.quarterly_balance_sheet.to_html()
    elif str(texts[0]).strip() == "CASH_FLOW":
        final_info = stock.quarterly_cashflow.to_html()
    elif str(texts[0]).strip() == "INCOME_STATEMENT":
        final_info = stock.quarterly_cashflow.to_html()
    elif str(texts[0]).strip() == "EARNINGS":
        #print(stock.get_earnings_trend())
        final_info = stock.get_earnings_dates().to_html()
    elif str(texts[0]).strip() == "QUOTE":
        x = get_quote(str(texts[1]).strip())["quote"]["ap"]
        final_info = x
    else:
        final_info = stock.info
    for d in range(3):
        try:
            msg = analyzer.send_message(f"Take the user's last message and the information I am giving you which is the data they are looking for. Make a response that the user will see and understand. \n {str(texts[0]).strip()}:{final_info}")
            return msg.text
        except Exception as e:
            print(f"Execution #{d} failed, trying again")
            continue
    return f"{str(texts[0]).strip()}: {final_info}"

def FinChatReader(query):
    import requests

    url = "https://api.finchat.io/v1/query"

    payload = {
        "query": query,
        "history": [],
        "inlineSourcing": True,
        "stream": False,
        "generateChatTitle": True,
        "generateFollowUpQuestions": True
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 425c70b012164e65968182108f51df9c"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json())



def make_action(history, user):
    analyzer = model.start_chat(history = refine_chat_history(history, user))
    sol_finder = analyzer.send_message("From this chat, what action should be executed currently?\n DO NOT USE MARKDOWN OR OTHER TEXTUAL EDITS \n - creating investment plans/portfolios \n - trading stocks/assets directly.\n- changing user settings\n- ordering money transfers between accounts.\n- analysis of SEC and Earnings Data of Assets.\n - Rebalancing Portfolios and Making changes to investment plans.")
    print(sol_finder.text)
    return sol_finder.text

def send_message_and_get_response(input, history, user):
    # add code to have the model re-cap on the past knowledge and make a new judgement.
    """
    if ("yes" in input or "y" in input or "Yes" in input or "Y" in input):
        if ("confirm" in history.last().chatbot_response or "agree" in history.last().chatbot_response) and history.count() > 0:
            print("review past plan and make a solution.")
            # create a financial plan that could be registered in the system and executed. 
    """
    if history.count() != 0:
        if ("yes" in input or "y" in input or "Yes" in input or "Y" in input):
            if ("confirm" in history.last().chatbot_response or "agree" in history.last().chatbot_response) and history.count() > 0:
                print("review past plan and make a solution.")
                plan = make_action(history, user)
                if "creating investment plans/portfolios" in plan:
                    lk = create_financial_plan(user, history) 
                    if lk:
                        return "Financial Plan Created Successfully"
                elif "trading stocks/assets directly" in plan:
                    d = "None"
                    while True:
                        try:
                            d = find_and_make_trade(user, history)
                            if type(d) == str:
                                break    
                        except Exception:
                            continue
                    return d
                elif "analysis of SEC and Earnings Data of Assets" in plan:
                    ana = get_asset_data(history, user)
                    return ana
                # we have covered financial plans. We need to cover the following:
                # trading stocks/assets directly. 
                # changing user settings
                # ordering money transfers between accounts. 
                # analysis of SEC and Earnings Data of Assets. 
                # Rebalancing Portfolios and Making changes to Financial plans.
                
            else:
                print(history.count())
                print("processing")        
                response = model.start_chat(history=refine_chat_history(history, user))
                xt = response.send_message(input)
                print(xt.text)
                return xt.text
        else:
            print(history.count())
            print("processing")        
            response = model.start_chat(history=refine_chat_history(history, user))
            xt = response.send_message(input)
            print(xt.text)
            return xt.text
    else:
        print(history.count())
        print("processing")
        response = model.start_chat(history=refine_chat_history(history, user))        
        xt = response.send_message(input)
        print(xt.text)
        return xt.text



def test_ai_connection():
    try:
        import pprint
        import google.generativeai as genai

        creds = load_creds()
        print(creds)

        genai.configure(credentials=creds)

        print()
        print('Available base models:', [m.name for m in genai.list_models()])
    except Exception:
        
        return False

test_ai_connection()
