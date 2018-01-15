import { Component, OnInit } from '@angular/core';

import { HelpService } from '../help.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-help',
  templateUrl: './help.component.html',
  styleUrls: ['./help.component.css']
})
export class HelpComponent implements OnInit {
  constructor(
    public globals: Globals,
    private helpService: HelpService
  ) {}

  ngOnInit() {
    this.getArticles();
  }
  
  getArticles() {
    if (!this.globals.helpArticles) {
      this.helpService.getArticles()
        .subscribe(resp => this.globals.helpArticles = resp.articles);
    }
  }

}
