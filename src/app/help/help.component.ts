import { Component, OnInit } from '@angular/core';

import { HelpService } from '../help.service';

@Component({
  selector: 'app-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.css']
})
export class HelpComponent implements OnInit {
  articles: any[] = null;
  
  constructor(private helpService: HelpService) { }

  ngOnInit() {
    this.getArticles()
  }
  
  getArticles() {
    if (!this.articles) {
      this.helpService.getArticles()
        .subscribe(resp => this.articles = resp);
    }
  }

}
