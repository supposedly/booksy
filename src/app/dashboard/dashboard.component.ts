import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';

import { MemberService } from '../member.service';

@Component({
  selector: 'app-dashboard',
  template: `
    <div id="container">
      <div id="spacer"></div>
      <app-generic-header [buttons]="buttons" [inbetween]="uID"></app-generic-header>
      <router-outlet></router-outlet>
    </div>
  `,
  styleUrls: ['./dashboard.component.css']
})
export class DashboardComponent implements OnInit {
  uID: string;
  buttons = [
    {text: 'items'},
    {text: 'holds'}
  ];
  
  constructor(private route: ActivatedRoute) {}
  
  ngOnInit() {
    this.uID = this.route.snapshot.firstChild.paramMap.get('uID');
  }

}
