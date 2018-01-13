import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-dash-header',
  templateUrl: './dash-header.component.html',
  styleUrls: ['./dash-header.component.css']
})
export class DashHeaderComponent {
  buttons = [
    {'text': 'items'},
    {'text': 'holds'}
  ]
  constructor() { }

}
