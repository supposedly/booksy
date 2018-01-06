import { Component, OnInit } from '@angular/core';
import { Globals } from '../session-info-globals';

@Component({
  selector: 'app-home-page',
  templateUrl: './home-page.component.html',
  styleUrls: ['./home-page.component.css']
})
export class HomePageComponent implements OnInit {
  constructor(public globals: Globals) {}
  
  ngOnInit() {}
}
