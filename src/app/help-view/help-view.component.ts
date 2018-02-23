import { Component, OnInit, Input } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Location } from '@angular/common';

import { HelpService } from '../help.service';

@Component({
  selector: 'app-help-view',
  templateUrl: './help-view.component.html',
  styleUrls: ['./help-view.component.css']
})
export class HelpViewComponent implements OnInit {
  id: string;
  article: string;

  constructor(
    public location: Location,
    private helpService: HelpService,
    private route: ActivatedRoute
  ) {}

  ngOnInit() {
    this.id = this.route.snapshot.paramMap.get('id');
    this.getArticle();
  }
  
  getArticle() {
    this.helpService.getArticle(this.id)
      .subscribe(resp => this.article = resp.help)
  }

}
