import { Component, OnInit } from '@angular/core';

import { LocationService } from '../location.service';
import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-media-search',
  templateUrl: './media-search.component.html',
  styleUrls: ['./media-search.component.css']
})
export class MediaSearchComponent implements OnInit {
  suggested: any[] = [];
  items: any[] = [];
  cont: number = 0;
  msg: string = 0;
  
  constructor(
    private globals: Globals,
    private locationService: LocationService,
    private memberService: MemberService
  ) {}

  ngOnInit() {
    this.getSuggestions();
 // this.getAllItems(); // Do I really want this or should I limit it just to searches?
  }
  
  getSuggestions() {
    this.memberService.getSuggestions(this.cont)
      .subscribe(res => this.suggested = res, err => this.msg = err.error?err.error:'Error.');
  }
  
  getAllItems() {
    this.locationService.getItems
  }

}
