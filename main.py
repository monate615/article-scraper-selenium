from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import pyperclip

import re

import tkinter as tk
from tkinter import messagebox

import time
import threading

import csv

article_url = r'https://www.thetakeout.com/category/news/'
hemingway_url = r'https://hemingwayapp.com/'
spam_checker_url = r'https://mailmeteor.com/spam-checker'

driver = webdriver.Chrome()
for i in range(4):
    driver.execute_script("window.open();")

wait = WebDriverWait(driver, 50)

_articels = []
_whole_articles = []
_hemingway_error_dicts = []
_spam_check_dicts = []

while True:
    try:
        driver.switch_to.window(driver.window_handles[0])
        driver.get(article_url)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li[class="article-item"]')))
        articles = driver.find_elements(By.CSS_SELECTOR, 'li[class="article-item"]')
        
        for article in articles:
            try:
                link = article.find_element(By.CSS_SELECTOR, 'a[cmp-ltrk="Home - Article List"]').get_attribute('data-mrf-link')
                driver.switch_to.window(driver.window_handles[1])
                driver.get(link)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-mrf-recirculation="Article - Text links"]')))
                sub_articles = driver.find_elements(By.CSS_SELECTOR, 'div[data-mrf-recirculation="Article - Text links"]')
                title_article = sub_articles[0]
                title = title_article.find_element(By.CSS_SELECTOR, 'h1[id="title-gallery"]').get_attribute('innerText')
                print(title)
                paragraphs = []
                para_elements = title_article.find_elements(By.CSS_SELECTOR, 'p')
                for para_element in para_elements:
                    paragraphs.append(para_element.get_attribute('innerText'))
                _sub_articles = []
                for sub_article in sub_articles[1:]:
                    sub_title = sub_article.find_element(By.CSS_SELECTOR, 'h2').get_attribute('innerText')
                    sub_para_elements = sub_article.find_elements(By.CSS_SELECTOR, 'p')
                    sub_paragraphs = []
                    for sub_para_element in sub_para_elements:
                        sub_paragraphs.append(sub_para_element.get_attribute('innerText'))
                    _sub_articles.append([sub_title, sub_paragraphs])

                _articels.append([title, paragraphs, _sub_articles])

                driver.switch_to.window(driver.window_handles[2])
                driver.get(hemingway_url)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]')))
                hemingway_editor = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
                driver.execute_script("""
    var element = arguments[0];
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
""", hemingway_editor)
                driver.execute_script("""
var parentElement = arguments[0];
var article = arguments[1];
                                      
var title = article[0];
var paragraphs = article[1];
var sub_articles = article[2];

var newH1 = document.createElement('h1');
newH1.innerText = title;
parentElement.appendChild(newH1);
                                      
paragraphs.forEach(function(paragraph) {
    var newP = document.createElement('p');
    newP.innerText = paragraph;
    parentElement.appendChild(newP);
});
sub_articles.forEach(function(sub_article) {
    var newH2 = document.createElement('h2');
    newH2.innerText = sub_article[0];
    parentElement.appendChild(newH2);
    sub_article[1].forEach(function(sub_paragraph) {
        var newP = document.createElement('p');
        newP.innerText = sub_paragraph;
        parentElement.appendChild(newP);
    });
});
""", hemingway_editor, _articels[-1])
                driver.refresh()
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[contenteditable="true"]')))
                hemingway_editor = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
                _whole_articles.append(hemingway_editor.get_attribute('innerText'))
                hemingway_repair_controls = hemingway_editor.find_elements(By.CSS_SELECTOR, 'span')
                hemingway_error_dict = {}
                hemingway_error_dict['red'] = []
                hemingway_error_dict['yellow'] = []
                hemingway_error_dict['lime'] = []
                hemingway_error_dict['sky'] = []
                hemingway_error_dict['violet'] = []
                for hemingway_repair_control in hemingway_repair_controls:
                    hemingway_repair_class = hemingway_repair_control.get_attribute('class')
                    if hemingway_repair_class.find('bg-red-200') != -1:
                        hemingway_error_dict['red'].append(hemingway_repair_control.get_attribute('innerText'))
                    elif hemingway_repair_class.find('bg-yellow-200') != -1:
                        hemingway_error_dict['yellow'].append(hemingway_repair_control.get_attribute('innerText'))
                    elif hemingway_repair_class.find('bg-lime-200') != -1:
                        hemingway_error_dict['lime'].append(hemingway_repair_control.get_attribute('innerText'))
                    elif hemingway_repair_class.find('bg-sky-200') != -1:
                        hemingway_error_dict['sky'].append(hemingway_repair_control.get_attribute('innerText'))
                    elif hemingway_repair_class.find('bg-violet-200') != -1:
                        hemingway_error_dict['violet'].append(hemingway_repair_control.get_attribute('innerText'))
                _hemingway_error_dicts.append(hemingway_error_dict)
                driver.switch_to.window(driver.window_handles[3])
                driver.get(spam_checker_url)
                pyperclip.copy(_whole_articles[-1])
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[id="spam-checker--input"]')))
                spam_checker_editor = driver.find_element(By.CSS_SELECTOR, 'div[id="spam-checker--input"]')
                # driver.execute_script('arguments[0].innerText = arguments[1];', spam_checker_editor, _whole_articles[-1])
                spam_checker_editor.click()
                actions = ActionChains(driver)
                actions.key_down(Keys.CONTROL).send_keys('a').key_up(Keys.CONTROL).perform()
                actions.key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
                time.sleep(0.5)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[class="hwt-highlights hwt-content"]')))
                spam_checker_editor = driver.find_element(By.CSS_SELECTOR, 'div[class="hwt-highlights hwt-content"]')
                spam_checker_error_controls = spam_checker_editor.find_elements(By.CSS_SELECTOR, 'mark')
                spam_checker_error_dict = {}
                spam_checker_error_dict['shady'] = []
                spam_checker_error_dict['money'] = []
                spam_checker_error_dict['urgency'] = []
                spam_checker_error_dict['unnatural'] = []
                spam_checker_error_dict['overpromise'] = []
                for spam_checker_error_control in spam_checker_error_controls:
                    spam_checker_error_class = spam_checker_error_control.get_attribute('class')
                    if spam_checker_error_class.find('spam-category-shady') != -1:
                        spam_checker_error_dict['shady'].append(spam_checker_error_control.get_attribute('innerText'))
                    elif spam_checker_error_class.find('spam-category-money') != -1:
                        spam_checker_error_dict['money'].append(spam_checker_error_control.get_attribute('innerText'))
                    elif spam_checker_error_class.find('spam-category-urgency') != -1:
                        spam_checker_error_dict['urgency'].append(spam_checker_error_control.get_attribute('innerText'))
                    elif spam_checker_error_class.find('spam-category-unnatural') != -1:
                        spam_checker_error_dict['unnatural'].append(spam_checker_error_control.get_attribute('innerText'))
                    elif spam_checker_error_class.find('spam-category-overpromise') != -1:
                        spam_checker_error_dict['overpromise'].append(spam_checker_error_control.get_attribute('innerText'))
                _spam_check_dicts.append(spam_checker_error_dict)
            except:
                ...
            finally:
                driver.switch_to.window(driver.window_handles[0])
        
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[id="next-page"]')))
        article_url = driver.find_element(By.CSS_SELECTOR, 'a[id="next-page"]').get_attribute('href')
        print(article_url)

    except:
        break